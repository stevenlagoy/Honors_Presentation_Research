from typing import List, Dict

from Paths import ROOT_URL
from MapEntity import MapEntity

class State(MapEntity):
    def __init__(self, name: str, population: int, demographics: Dict[str, float]):
        super().__init__(name, population, demographics)

    def __str__(self) -> str:
        return f"State: {super().__str__()}"
    
    def get_link(self) -> str:
        return f"{ROOT_URL}/state/{self.name.replace(" ","-")}/Overview"