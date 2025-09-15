#include "State.h"

State::State(std::string name, int population, std::map<std::string, float> demographics)
    : MapEntity(name, population, demographics) {
}

