#include "County.h"

County::County(std::string name, int population, std::map<std::string, float> demographics, State state)
    : MapEntity(name, population, demographics), state(state) {
}

State County::getState() const {
    return this->state;
}