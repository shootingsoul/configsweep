# SPDX-FileCopyrightText: Coypright © 2024 Shooting Soul Ventures, LLC <jg@shootingsoul.com>
# SPDX-License-Identifier: MIT

from enum import Enum
from typing import Any, Union, List, Tuple
import itertools
from configsweep.sweep import Sweep
from dataclasses import is_dataclass
from operator import attrgetter


class SweepDag:
    """
    A dag of sweep items from the given config
    Each node in the dag has a list of combinations ot process
    Thus, the root node has all the combionations to process for the entire config

    First the DAG nodes are built
    Second, each child node is sorted according to the priority
    Third, the combinations are built in the priorty order

    NOTE: this is constantly modifying the config passed in 
    and keeps references to objects in the config passed in
    """

    def __init__(self, config: Any):
        self.config = config
        # need a single value for combo algorithm
        self.root_node = SweepDag.Node(Sweep([None]))
        self.build_nodes(self.root_node, 0, "", None, None, None, None, config)
        self.sort_priority(self.root_node)
        self.build_combos(self.root_node)

    class ComboElement:
        def __init__(self, node, value_index: int, next=None):
            self.node: SweepDag.Node = node
            self.value_index: int = value_index
            self.next: SweepDag.ComboElement = next

        def value(self):
            return self.node.values[self.value_index]

        def value_description(self, with_name: bool = False):
            # build description for sweep item replaced
            value = self.value()
            value_desc = _short_value_description(value)
            if not value_desc:
                value_desc = f"<complex_value>[{self.value_index}]"
            return f"{self.node.object_name}={value_desc}" if with_name else value_desc

        def last_value_description(self, with_name: bool = False):
            last = self
            while last.next is not None:
                last = last.next
            return last.value_description(with_name)

    class Node:
        def __init__(self,
                     sweep: Sweep,
                     parent=None,
                     parent_value_index: int = None,
                     object_name: str = None,
                     attribute_name: str = None,
                     key_name: str = None,
                     list_index: int = None,
                     object=None):
            self.sweep = sweep  # original sweep item in the config
            self.parent: SweepDag.Node = parent
            self.parent_value_index: int = parent_value_index
            self.object_name: str = object_name
            self.attribute_name = attribute_name  # also indicates obj is a class
            self.key_name = key_name  # also indicates obj is a dict
            self.list_index = list_index  # also indicates obj is a list
            self.object = object
            self.priority = sweep.priority
            # sweep node values to sweep through must be a non-empty list
            if sweep.values is None or not isinstance(sweep.values, list) or not len(sweep.values):
                raise ValueError(
                    f"{object_name} Sweep values must contain a non-empty list")
            self.values = sweep.values
            self.child_nodes: List[SweepDag.Node] = []
            self.combos: List[List[SweepDag.ComboElement]] = []

    def build_nodes(self, parent, parent_value_index: int, object_name: str, attribute_name: str, key_name: str, list_index: int, object, value):
        """
        Pull out the DAG of sweep nodes from config file
        Traverse through all dicts, lists and dataclasses in the config to extract the sweep node DAG
        The DAG only contains sweep nodes with references back to the original config
        """
        if isinstance(value, Sweep):
            # check if came from a tuple/set.  Can't swap out values in that
            # set/tuple can't contain a sweep object (not hashable), so this should never come up in theory
            if isinstance(object, (set, tuple, frozenset)):
                raise TypeError(
                    f"Can't sweep items in a tuple or set.  See if item {object_name} can be converted to a list.")

            node = SweepDag.Node(value, parent, parent_value_index,
                                 object_name, attribute_name, key_name, list_index, object)
            parent.child_nodes.append(node)
            # support sweep within sweep (could be nested right away or later on)
            # cut out current sweep node, set it as the parent and use it's values to then proceed as normal
            parent = node
            value = value.values
            for idx, next_value in enumerate(value):
                if isinstance(next_value, Sweep):
                    raise TypeError((f"{object_name} Sweep value can't be another sweep directly.  "
                                     "Use one Sweep item with a list of merged values or make an array to sweep an element in the array"))
                self.build_nodes(parent, idx, object_name,
                                 None, None, idx, value, next_value)
        elif isinstance(value, dict):
            for name, next_value in value.items():
                next_object_name = f"{object_name}.{name}" if len(
                    object_name) else name
                self.build_nodes(parent, parent_value_index,
                                 next_object_name, None, name, None, value, next_value)
        elif is_dataclass(value):
            for name, next_value in vars(value).items():
                # skip dunders
                if not name.startswith('__'):
                    next_object_name = f"{object_name}.{name}" if len(
                        object_name) else name
                    self.build_nodes(
                        parent, parent_value_index, next_object_name, name, None, None, value, next_value)
        elif isinstance(value, (list, set, tuple, frozenset)):
            # it's ok to go through tuple/set, but not to sweep items inside a tuple or set
            for idx, next_value in enumerate(value):
                self.build_nodes(parent, parent_value_index,
                                 f"{object_name}[{idx}]", None, None, idx, value, next_value)

    def sort_priority(self, node):
        """
        Sort the children of each node by priority 
        This ensures sweep items are processed in the correct order to keep items together across combinations
        """
        if len(node.child_nodes):
            for child in node.child_nodes:
                self.sort_priority(child)
            node.child_nodes.sort(key=attrgetter('priority'), reverse=True)

    def build_combos(self, node):
        """
        Builds the combinations for each node in the dag with children already sorted correctly

        Handle nested sweeps
        If a sweep index has child sweeps then take the product of those children
        Also keep a list for the combo element to know all the nested replacements to make down stream

        The base case is there are no kids, so just use the sweep values as the combos
        """
        if not len(node.child_nodes):
            # base case optimized for when no kids
            # value is the combo
            node.combos = [[SweepDag.ComboElement(
                node, i)] for i in range(len(node.values))]
            return
        else:
            for child in node.child_nodes:
                self.build_combos(child)

            for value_index in range(len(node.values)):
                index_had_a_child = False
                # when child sweeps share the same parent index
                # then take the product of those children
                a = []
                for child in node.child_nodes:
                    if child.parent_value_index == value_index:
                        sub_list = []
                        for child_combo in child.combos:
                            # need to replace for each child combo current element and the child element
                            sub_list.append([SweepDag.ComboElement(
                                node, value_index, ce) for ce in child_combo])
                        a.append(sub_list)
                        index_had_a_child = True
                if index_had_a_child:
                    p = list(itertools.product(*a))
                    # product gives a tuple of items from each list
                    # however, child elements will be a list of combo elements
                    # flatten it to a list of combo elements
                    for combo_tuple in p:
                        flat = []
                        for i in combo_tuple:
                            # know it will be a plain list from the product function
                            if isinstance(i, list):
                                for j in i:
                                    flat.append(j)
                            else:
                                flat.append(i)
                        node.combos.append(flat)
                else:
                    # base case - append the value as the combo
                    node.combos.append(
                        [SweepDag.ComboElement(node, value_index)])

    def apply_combo_to_config(self, combo_index: int) -> List[str]:
        """
        Apply all the values in the combo to the config
        So we go through the config and swap out all the right values in all the right places

        Each element in the combo has a reference to the config to replace 
        and a list sub elements to replace as well
        """
        combo = self.root_node.combos[combo_index]
        description_list = []
        for element in combo:
            element_description_list = []
            # make all replacements down the chain for nested sweeps
            while element is not None:
                node = element.node
                value = node.values[element.value_index]
                object = node.object
                if object is not None:
                    if node.attribute_name is not None:
                        setattr(object, node.attribute_name, value)
                    elif node.key_name is not None:
                        object[node.key_name] = value
                    else:
                        object[node.list_index] = value
                    element_description_list.append(element.value_description(with_name=True))
                    # if element.next is None:
                    #     # use last element in chain for the description
                    #     element_description_list.append(
                    #         element.value_description(with_name=True))
                    # else:
                    #     element_description_list.append(node.object_name)
                element = element.next
            description_list.append(' & '.join(element_description_list))
        return description_list

    def apply_sweep_to_config(self):
        """
        Put the sweep objects back into the config
        i.e. put it back to how it was originally
        """
        self._apply_sweep(self.root_node)

    def _apply_sweep(self, node):
        if node is None:
            return

        object = node.object
        if object is not None:
            value = node.sweep
            if node.attribute_name is not None:
                setattr(object, node.attribute_name, value)
            elif node.key_name is not None:
                object[node.key_name] = value
            else:
                object[node.list_index] = value

        for child in node.child_nodes:
            self._apply_sweep(child)


def _short_value_description(value: Any) -> Union[str, None]:
    # guess at a short description for the value
    # return None for can't decide/too long
    # put a limit on the size
    LIMIT = 100

    description = None
    if isinstance(value, (str, bool, float, int, Enum)):
        description = str(value)
        if len(description) > LIMIT:
            description = description[:LIMIT - 3] + "..."
    elif isinstance(value, (list, dict, set, tuple)):
        # don't bother for collections
        pass
    else:
        # see if we can get a description of the class that is short
        description = str(value)
        if len(description) > LIMIT:
            description = None  # nevermind, we tried

    return description
