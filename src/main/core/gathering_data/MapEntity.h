#ifndef MAP_ENTITY_H
#define MAP_ENTITY_H

#include <string>
#include <map>

class MapEntity {
private:
    std::string name;
    int population;
    std::map<std::string, float> demographics;
public:
    MapEntity(std::string name, int population, std::map<std::string, float> demographics);

    std::string getName() const;
    int getPopulation() const;
    std::map<std::string, float> getDemographics() const;
};

#endif