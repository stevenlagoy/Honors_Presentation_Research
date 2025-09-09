from typing import List, Dict, Any
import json
import os

from Demographic import Demographic, DemographicGroup
from Descriptor import Descriptor

class MapEntity:
    def __init__(self, name: str, population: int, demographics: Dict[Demographic, float], descriptors: List[Descriptor] = []):
        self.name = name
        self.population = population
        self.demographics = demographics
        self.descriptors = descriptors

    def descriptor_demographics(self) -> Dict[Demographic, float]:
        result: Dict[Demographic, float] = {}
        for descriptor in self.descriptors:
            for demographic in descriptor.effects:
                result[demographic] += descriptor.effect_on(demographic)
        return result

class Nation(MapEntity):
    _instance = None

    @staticmethod
    def get_instance() -> "Nation":
        if Nation._instance is None:
            Nation._instance = Nation(0, {}, [])
        return Nation._instance

    @staticmethod
    def from_json(json: Dict[str, Any]) -> "Nation | None":
        try:
            nation = Nation.get_instance()
            nation.population = json['population']
            nation.descriptors = []
            for group in json["demographics"]:
                for name in json["demographics"][group]:
                    d = Demographic(name, DemographicGroup(group))
                    nation.demographics[d] = json["demographics"][group][name]
        except KeyError as e:
            print(f"Encountered an error while reading Nation json: {e}")
            return None
    
    def __init__(self, population: int, demographics: Dict[Demographic, float], descriptors: List[Descriptor] = []):
        super().__init__("United States", population, demographics, descriptors)

class State(MapEntity):
    def __init__(self, name: str, population: int, demographics: Dict[Demographic, float], descriptors: List[Descriptor] = []):
        super().__init__(name, population, demographics, descriptors)
        self.nation = Nation.get_instance()

    def __str__(self):
        return f"State: {self.name}, population {self.population}"
    
    def descriptor_demographics(self) -> Dict[Demographic, float]:
        this_demographics = super().descriptor_demographics()
        nation_demographics = self.nation.descriptor_demographics()
        return {k : this_demographics.get(k, 0) + nation_demographics.get(k, 0) for k in set(this_demographics) | set(nation_demographics)} # Combine dictionaries and take the sum when keys overlap

class County(MapEntity):
    def __init__(self, state: State, name: str, population: int, demographics: Dict[Demographic, float], descriptors: List[Descriptor] = []):
        super().__init__(name, population, demographics, descriptors)
        self.state = state

    def __str__(self):
        return f"County: {self.name}, state: {self.state.name}, population {self.population}"
    
    def descriptor_demographics(self) -> Dict[Demographic, float]:
        this_demographics = super().descriptor_demographics()
        state_demographics = self.state.descriptor_demographics()
        return {k : this_demographics.get(k, 0) + state_demographics.get(k, 0) for k in set(this_demographics) | set(state_demographics)} # Combine dictionaries and take the sum when keys overlap

def _data_to_json(filename) -> Dict[str, Any]:
    with open(filename) as file:
        contents = file.read()
    data = json.loads(contents)
    return data

def read_nation():
    data = _data_to_json("src\\main\\resources\\nation.json")
    Nation.from_json(data) # Saves to Nation._instance

states: List[State] = []
def read_states():
    # TODO: Determine how to store demographics: as dictionary of subdictionaries, or as flat list? 
    global states
    states = []
    for directory in os.listdir("src\\main\\resources"):
        if not '.' in directory:
            data_file = [file for file in os.listdir("src\\main\\resources\\" + directory) if '.' in file][0]
            with open("src\\main\\resources\\" + directory + "\\" + data_file) as data:
                j = json.loads(data.read())
                demographics: Dict[Demographic, float] = {}
                for group in j["demographics"]:
                    for d in j["demographics"][group]:
                        demographics[d] = j["demographics"][group][d]
                states.append(State(j["name"], j["population"], demographics))

counties = []
def read_counties():
    global counties
    counties = []
    if not len(states):
        return None 
    for state_name in os.listdir("src\\main\\resources"):
        if not '.' in state_name:
            state = [s for s in states if s.name.lower().replace(" ","_") == state_name][0]
            for county_file in [i for i in os.listdir("src\\main\\resources\\" + state_name + "\\counties") if '.' in i]:
                with open("src\\main\\resources\\" + state_name + "\\counties\\" + county_file) as data:
                    j = json.loads(data.read())
                    counties.append(County(state, j["name"], j["population"], j["demographics"]))

# On Import
print("Reading Map Entities...")
read_nation()
read_states()
read_counties()
print(f"{len(states)+len(counties)+1} Map Entities read successfully")