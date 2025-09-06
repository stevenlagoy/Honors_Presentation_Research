#ifndef COUNTY_H
#define COUNTY_H

#include "State.h"

class County : public MapEntity {
private:
    State state;
public:
    County(std::string name, int population, std::map<std::string, float> demographics, State state);

    State getState() const;
};

#endif