# Config Sweep

Sweep through config settings with nested values to sweep
- Sweep existing yaml, json or dataclass configs
- Supports nested sweep definitions
- Prioritize sweeps to minimize cache thrash
- Use typed configs for dynamic systems with the create_affiliate protocol
- Save sweep and dataclass configs with ClassifiedJSON

```
pip install 'configsweep[classifiedjson]'
```
```python
from configsweep import Sweep, Sweeper
from classifiedjson import dump

# set priorty on datasources to sweep through those values first
# to avoid reloading the same data
sweep_config = { "strategy": Sweep([
               {"name": "strategy_one", "max": 10000},
               {"name": "strategy_two", "min": Sweep([10,20,30]), "max": Sweep([10000,90000])}
               ]),
            "datasources": Sweep(["en", "es", "de", "fr"], priority=1)
        }

for combo in Sweeper(sweep_config):
    print(combo.config)

with open('sweep_config.json', 'w') as f:
    dump(sweep_config, f)
```
output
```
{'strategy': {'name': 'strategy_one', 'max': 10000}, 'datasources': 'en'}
{'strategy': {'name': 'strategy_two', 'min': 10, 'max': 10000}, 'datasources': 'en'}
{'strategy': {'name': 'strategy_two', 'min': 10, 'max': 90000}, 'datasources': 'en'}
{'strategy': {'name': 'strategy_two', 'min': 20, 'max': 10000}, 'datasources': 'en'}
{'strategy': {'name': 'strategy_two', 'min': 20, 'max': 90000}, 'datasources': 'en'}
{'strategy': {'name': 'strategy_two', 'min': 30, 'max': 10000}, 'datasources': 'en'}
{'strategy': {'name': 'strategy_two', 'min': 30, 'max': 90000}, 'datasources': 'en'}
{'strategy': {'name': 'strategy_one', 'max': 10000}, 'datasources': 'es'}
{'strategy': {'name': 'strategy_two', 'min': 10, 'max': 10000}, 'datasources': 'es'}
{'strategy': {'name': 'strategy_two', 'min': 10, 'max': 90000}, 'datasources': 'es'}
{'strategy': {'name': 'strategy_two', 'min': 20, 'max': 10000}, 'datasources': 'es'}
{'strategy': {'name': 'strategy_two', 'min': 20, 'max': 90000}, 'datasources': 'es'}
{'strategy': {'name': 'strategy_two', 'min': 30, 'max': 10000}, 'datasources': 'es'}
{'strategy': {'name': 'strategy_two', 'min': 30, 'max': 90000}, 'datasources': 'es'}
{'strategy': {'name': 'strategy_one', 'max': 10000}, 'datasources': 'de'}
{'strategy': {'name': 'strategy_two', 'min': 10, 'max': 10000}, 'datasources': 'de'}
{'strategy': {'name': 'strategy_two', 'min': 10, 'max': 90000}, 'datasources': 'de'}
{'strategy': {'name': 'strategy_two', 'min': 20, 'max': 10000}, 'datasources': 'de'}
{'strategy': {'name': 'strategy_two', 'min': 20, 'max': 90000}, 'datasources': 'de'}
{'strategy': {'name': 'strategy_two', 'min': 30, 'max': 10000}, 'datasources': 'de'}
{'strategy': {'name': 'strategy_two', 'min': 30, 'max': 90000}, 'datasources': 'de'}
{'strategy': {'name': 'strategy_one', 'max': 10000}, 'datasources': 'fr'}
{'strategy': {'name': 'strategy_two', 'min': 10, 'max': 10000}, 'datasources': 'fr'}
{'strategy': {'name': 'strategy_two', 'min': 10, 'max': 90000}, 'datasources': 'fr'}
{'strategy': {'name': 'strategy_two', 'min': 20, 'max': 10000}, 'datasources': 'fr'}
{'strategy': {'name': 'strategy_two', 'min': 20, 'max': 90000}, 'datasources': 'fr'}
{'strategy': {'name': 'strategy_two', 'min': 30, 'max': 10000}, 'datasources': 'fr'}
{'strategy': {'name': 'strategy_two', 'min': 30, 'max': 90000}, 'datasources': 'fr'}
```

---

## Installation

Python >=3.8

```
pip install 'configsweep[classifiedjson]'
```

If you don't need support to save sweep or dataclass configs to a file/string, you can install without classifiedjson.
```
pip install configsweep
```

---

## Examples

### Sweep yaml
```python
import yaml
from configsweep import Sweep, Sweeper

data = { "start": 2024, "state": 'FL'}

with open('myconfig.yml', 'w',) as f:
    yaml.dump(data, f, sort_keys=False) 

with open('myconfig.yml', 'r') as f:
    config = yaml.safe_load(f)

config['state'] = Sweep(['FL', 'MI', 'IN', 'AL'])
for combo in Sweeper(config):
    print(combo.config)
```
output
```
{'start': 2024, 'state': 'FL'}
{'start': 2024, 'state': 'MI'}
{'start': 2024, 'state': 'IN'}
{'start': 2024, 'state': 'AL'}
```

---

### Sweep dataclass
```python
from dataclasses import dataclass
from enum import Enum
from configsweep import Sweep, Sweeper
from classifiedjson import dumps, loads

class Direction(Enum):
    LEFT = 0
    RIGHT = 1
    
@dataclass
class AlternateAfter:
    left_times: int = 2
    right_times: int = 3
    starting_direction: Direction = Direction.RIGHT

sweep_config = AlternateAfter()
sweep_config.starting_direction = Sweep([Direction.RIGHT, Direction.LEFT])

# save off sweep config
sweep_json = dumps(sweep_config)


for combo in Sweeper(sweep_config):
    print(combo.config.starting_direction)
    
    # save off each combo
    config_json = dumps(combo.config)
```
output
```
Direction.RIGHT
Direction.LEFT
```

---

## Typed Config with the create_affiliate protocol and ClassifiedJSON

Using typed configs makes it easier to work with to get intelli-sense, docstrings, etc.  However, there is a need to instantiate the system being configured.  Adding the function create_affiliate to every config class does just that.  The function create_affiliate creates an instance of the class it configures, i.e. it's affiliate.  The config can pass itself to the affiliate class or pass all needed values to the affiliate class.  The config acts as a factory for the affiliate class.

This is useful for handling union and subclass scenarios where you don't know the exact type ahead of time.
```
  loss: Hinge | MSE | L1 ...
  metric: MetricBase
```
When creating a system from a config, rather than having a separate factory class or large case/if statement to handle the various union/subclass scenarios, the config itself creates the correct affiliate class.

In addition to typed config and the create_affiliate protocol, there still needs to be the ability to save a config for reuse later.  This is where typed serialization such as ClassifiedJSON comes in.  ClassifiedJSON supports serializing typed python classes, such as dataclasses to json strings and deserialized back into the same typed pthon classes.

Thus, instead of dealing with large, untyped datastructures and yaml files, config can now be managed with typed python classes with type-hints, intelli-sense, docstrings, etc.

```python
# Psuedo-code for typed config with the create_affiliate protocol and ClassifiedJSON

# in this case, the config pass in all needed values to create it's affiliate
class FavorLeftStrategy(GoalieStrategy):
    def __init__(self, times: int):
        super().__init__('favor left')
        self._times = times
    ...

@dataclass
class FavorLeftConfig:
    times: int = 2

    def create_affiliate(self) -> FavorLeftStrategy:
        return FavorLeftStrategy(self.times)

# in this case, the config passes itself to the affiliate it creates
class AlternateAfterStrategy(GoalieStrategy):
    def __init__(self, config: AlternateAfter):
        super().__init__('aleternate after')
        self._config = config
    ...

@dataclass
class AlternateAfterConfig:
    left_times: int = 2
    
    def create_affiliate(self) -> AlternateAfterStrategy:
        return AlternateAfterStrategy(self)

# config with a union
@dataclass
class PkConfig:
    goalie_strategy: FavorLeft | AlternateAfter
    ...

def play_pk(config: PkConfig):
    goalie = config.goalie_strategy.create_affiliate()
    ...

# build up the config with typed code . . .
left = FavorLeft(5)
config = PkConfig(left)

# save off the config
serialized_json = classifiedjson.dumps(config)

#... tempus fugit...

# now use the config
config = classifiedjson.loads(serialized)
play_pk(config)
```

---

### Example of typed config with create_affiliate protocol and ClassifiedJSON

```python
from dataclasses import dataclass
from enum import Enum
from configsweep import Sweep, Sweeper
from classifiedjson import dumps, loads


class Direction(Enum):
    LEFT = 0
    RIGHT = 1

###################################
# Strategy sessions

class GoalieStrategy:
    def __init__(self, name: str):
        self.name = name

    def go_direction(self) -> Direction:
        pass

class FavorLeftStrategy(GoalieStrategy):
    def __init__(self, times: int):
        super().__init__('favor left')
        self._times = times
        self._counter = 0

    def go_direction(self) -> Direction:
        self._counter += 1
        if self._counter % self._times == 0:
            return Direction.RIGHT
        else:
            return Direction.LEFT

@dataclass
class FavorLeft:
    times: int = 2

    def create_affiliate(self) -> FavorLeftStrategy:
        return FavorLeftStrategy(self.times)


class AlternateAfterStrategy(GoalieStrategy):
    def __init__(self, config: AlternateAfter):
        super().__init__('aleternate after')
        self.config = config
        self.counter = 0
        self.next_direction = config.starting_direction

    def go_direction(self) -> Direction:
        direction = self.next_direction
        self.counter += 1
        if direction == Direction.LEFT and self.counter == self.config.left_times:
            self.next_direction = Direction.RIGHT
            self.counter = 0
        elif direction == Direction.RIGHT and self.counter == self.config.right_times:
            self.next_direction = Direction.LEFT
            self.counter = 0
 
        return direction

@dataclass
class AlternateAfter:
    left_times: int = 2
    right_times: int = 3
    starting_direction: Direction = Direction.RIGHT

    def create_affiliate(self) -> AlternateAfterStrategy:
        return AlternateAfterStrategy(self)


#######################
# strikers

@dataclass
class Striker:
    name: str
    strikes: list[int]
    
       
ronaldo = Striker('ronaldo', [0,1,0,0,1,0,1,0,1,0,1,1,1,1,1])
mbappe  = Striker('mbappe', [0,1,0,1,-1,0,-1,0,1,1,1,0,0,-1,0,-1])


###################
# Game Time!

@dataclass
class PkConfig:
    striker: Striker
    goalie_strategy: FavorLeft | AlternateAfter

def play_pk(config: PkConfig):
    striker = config.striker
    goalie = config.goalie_strategy.create_affiliate()
    
    scores = 0
    saves = 0
    for strike in striker.strikes:
        goalie_direction = goalie.go_direction()
        if strike == -1: # cheat code!
            scores += 1
        else:
            strike_direction = Direction(strike)
            if strike_direction == goalie_direction:
                saves += 1
            else:
                scores += 1
    return scores, saves


alternate_after = AlternateAfter()
alternate_after.left_times = Sweep(list(range(1, 5)))
alternate_after.right_times = Sweep(list(range(1, 5)))
config = PkConfig(Sweep([ronaldo, mbappe]), 
                  Sweep([
                        FavorLeft(Sweep([2,3,4])),
                        alternate_after
                        ]))

most_scores = None
most_config = None
for combo in Sweeper(config):
    config = combo.config
    scores, saves = play_pk(config)
    if most_scores is None or scores > most_scores:
        most_scores = scores
        most_config = config

print(f"most_scores={most_scores} ({most_config.striker.name})")
print(f"worst goalie strategy = {most_config.goalie_strategy}")
most_json = dumps(most_config)
#... tempus fugit...
config = loads(most_json)
#play back the most scores
scores, saves = play_pk(config)
print(f"scores={scores} ({config.striker.name})")
```
output
```
most_scores=13 (mbappe)
worst goalie strategy = AlternateAfter(left_times=2, right_times=3, starting_direction=<Direction.RIGHT: 1>)
scores=13 (mbappe)
```


