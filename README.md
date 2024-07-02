# Config Sweep

Sweep through config settings with nested values to sweep
- Sweep existing yaml, json or dataclass configs
- Supports nested sweep definitions
- Prioritize sweeps to minimize cache thrash
- Config dynamic systems with AffiliateClass
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

### Affiliate Class Pattern

The affiliate class pattern separates the config from the algorithm being configured.  The config is setup with a class variable for the algorithm class it configures.  This way, the config acts as a factory for the algorithm class.

For systems with lots of dynamic / union-style components, this allows for working with typed configuration with type-hints, intelli-sense, docstrings, etc. as opposed to working with large, untyped data structures for config.  

```python
# Psuedo-code for affiliate class pattern

class FavorLeft(AffiliateClass):
    times: int = 2
    ...

class FavorLeftStrategy(GoalieStrategy):
    def __init__(self, config: FavorLeft):
        super().__init__('favor left')
        self.config = config
    ...

FavorLeft._affiliate_cls = FavorLeftStrategy


class AlternateAfter(AffiliateClass):
    left_times: int = 2
    ...

class AlternateAfterStrategy(GoalieStrategy):
    def __init__(self, config: AlternateAfter):
        super().__init__('aleternate after')
        self.config = config
    ...

AlternateAfter._affiliate_cls = AlternateAfterStrategy


class PkConfig:
    goalie_strategy: FavorLeft | AlternateAfter
    ...

def play_pk(config: PkConfig):
    goalie = config.goalie_strategy.create_affiliate()
    ...
```

---

### Config dynamic system with AffiliateClass (full concrete example)

```python
from dataclasses import dataclass
from enum import Enum
from configsweep import Sweep, Sweeper, AffiliateClass
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

@dataclass
class FavorLeft(AffiliateClass):
    times: int = 2

class FavorLeftStrategy(GoalieStrategy):
    def __init__(self, config: FavorLeft):
        super().__init__('favor left')
        self.config = config
        self.counter = 0

    def go_direction(self) -> Direction:
        self.counter += 1
        if self.counter % self.config.times == 0:
            return Direction.RIGHT
        else:
            return Direction.LEFT

FavorLeft._affiliate_cls = FavorLeftStrategy

@dataclass
class AlternateAfter(AffiliateClass):
    left_times: int = 2
    right_times: int = 3
    starting_direction: Direction = Direction.RIGHT

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

AlternateAfter._affiliate_cls = AlternateAfterStrategy

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

# save off the most config
most_json = dumps(most_config)
```
output
```
most_scores=13 (mbappe)
worst goalie strategy = AlternateAfter(left_times=2, right_times=3, starting_direction=<Direction.RIGHT: 1>)
```


