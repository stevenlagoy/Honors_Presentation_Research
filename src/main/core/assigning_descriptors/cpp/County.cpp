#include "County.h"
#include <algorithm>

map<string, float> County::recalculate() {
    this->descDemographics.clear();
    for (auto desc = descriptors.begin(); desc != descriptors.end(); ++desc) {
        for (auto effect : desc->getEffects()) {
            this->descDemographics[effect.first] += effect.second;
        }
    }
    return descDemographics;
}

County::County(string name, string state, int population, map<string, float> demographics, vector<Descriptor> descriptors)
    : name{name}, state{state}, population{population}, demographics{demographics}, descDemographics{}, descriptors{descriptors} {
    this->recalculate();
}

string County::getName() const {
    return this->name;
}

string County::getState() const {
    return this->state;
}

map<string, float> County::getDemographics() const {
    return this->demographics;    
}

map<string, float> County::descriptorDemographics() const {
    return this->descDemographics;
}

float County::getDemographic(string demographic) const {
    return this->demographics.at(demographic);
}

vector<Descriptor> County::getDescriptors() const {
    return this->descriptors;
}

bool County::hasDescriptor(Descriptor d) const {
    return std::count(descriptors.begin(), descriptors.end(), d);
}

vector<Descriptor> County::addDescriptor(Descriptor d) {
    this->descriptors.emplace_back(d);
    return this->descriptors;
}

vector<Descriptor> County::removeDescriptor(Descriptor d) {
    auto newEnd = std::remove(descriptors.begin(), descriptors.end(), d);
    descriptors.erase(newEnd, descriptors.end());
    return this->descriptors;
}

string County::toString() const {
    string result = "";
    result += this->name + ", " + this->state + " | population: " + std::to_string(population) + " | descriptors: [";
    for (size_t i = 0; i < descriptors.size(); i++) {
        result += descriptors.at(i).getName() + ", ";
    }
    result += "];";
    return result;
}

bool County::operator<(const County& other) const {
    return std::tie(state, name) < std::tie(other.state, other.name);
}


std::ostream& operator<<(std::ostream& os, const County& obj) {
    os << obj.toString();
    return os;
}