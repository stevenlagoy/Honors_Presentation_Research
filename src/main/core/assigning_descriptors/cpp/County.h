#ifndef COUNTY_H
#define COUNTY_H

#include <string>
using std::string;
#include <map>
using std::map;
#include <vector>
using std::vector;
#include "Descriptor.h"
#include <ostream>

class County {
private:
    string name;
    string state;
    int population;
    map<string, float> demographics;
    map<string, float> descDemographics;
    vector<Descriptor> descriptors;
    public:
    County(string name, string state, int population, map<string, float> demogaphics, vector<Descriptor> descriptors = {});
    string getName() const;
    string getState() const;
    map<string, float> getDemographics() const;
    map<string, float> descriptorDemographics() const;
    float getDemographic(string demographic) const;
    vector<Descriptor> getDescriptors() const;
    bool hasDescriptor(Descriptor d) const;
    vector<Descriptor> addDescriptor(Descriptor d);
    vector<Descriptor> removeDescriptor(Descriptor d);
    map<string, float> recalculate();
    string toString() const;
    bool operator<(const County& other) const;
    friend std::ostream& operator<<(std::ostream& os, const County& obj);
};

#endif