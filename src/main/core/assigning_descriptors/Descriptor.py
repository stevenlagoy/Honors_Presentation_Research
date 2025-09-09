from typing import Dict, List

from Demographic import Demographic

'''
Every area in the nation has at least two descriptors: one base for the nation itself, and one for the state it is in.
Descriptors are additive. Adding all the descriptors' effects for an area should give simple percentages for each demographic in that area.
The addition of all descriptors should not result in a value below zero.

nation = { "demographic" : 0.5 }
state = { "demographic" : -0.25 }
county = { "demographic" : 0.125 }
In this case, "demographic" in the county will have a percentage membership of 0.375, or 37.5%.

Any given county is likely to have many more descriptors than this.

'''
class Descriptor:

    def __init__(self, name: str, effects: Dict[Demographic, float], eliminatiable = True):
        self.name: str = name
        self.effects: Dict[Demographic, float] = effects
        descriptors.append(self)
    
    def effect_on(self, demographic: Demographic) -> float:
        return self.effects[demographic]

descriptors: List[Descriptor] = []