from typing import Dict

from MapEntity import MapEntity

class Nation(MapEntity):
    def __init__(self, name: str, population: int, demographics: Dict[str, float]):
        super().__init__(name, population, demographics)

    def __str__(self) -> str:
        return f"Nation: {super().__str__()}"