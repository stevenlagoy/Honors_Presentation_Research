from typing import Dict

class MapEntity:
    def __init__(self, name: str, population: int, demographics: Dict[str, float]):
        self.name = name
        self.population = population
        self.demographics = demographics
    
    def __str__(self) -> str:
        return f"name: {self.name}, population: {self.population}, demographics: {self.demographics}"