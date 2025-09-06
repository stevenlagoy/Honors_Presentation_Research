#include "MapEntity.h"

MapEntity::MapEntity(std::string name, int population, std::map<std::string, float> demographics) {
    this->name = name;
    this->population = population;
    this->demographics = demographics;
}

std::string MapEntity::getName() const {
    return this->name;
}

int MapEntity::getPopulation() const {
    return this->population;
}

std::map<std::string, float> MapEntity::getDemographics() const {
    return this->demographics;
}