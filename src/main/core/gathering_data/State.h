#ifndef STATE_H
#define STATE_H

#include "MapEntity.h"

class State : public MapEntity {
public:
    State(std::string name, int population, std::map<std::string, float> demographics);
};

#endif