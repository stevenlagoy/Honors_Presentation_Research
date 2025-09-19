#include "Descriptor.h"

Descriptor::Descriptor(string name, map<string, float> effects, bool fixed)
    : name{name}, effects{effects}, fixed{fixed} {}

string Descriptor::getName() const {
    return this->name;
}

map<string, float> Descriptor::getEffects() const {
    return this->effects;
}

float Descriptor::getEffect(string demographic) const {
    return this->effects.at(demographic);
}

float Descriptor::setEffect(string demographic, float effect) {
    this->effects.at(demographic) = effect;
    return effect;
}

float Descriptor::addEffect(string demographic, float effect) {
    float prior = this->effects.at(demographic);
    return this->setEffect(demographic, prior + effect);
}

bool Descriptor::isFixed() const {
    return this->fixed;
}

bool Descriptor::operator==(const Descriptor& other) const {
    return this->name == other.name &&
           this->effects == other.effects &&
           this->fixed == other.fixed;
}

string Descriptor::toString() const {
    string result = "";
    result += "\"" + name + "\" : {";
    for (const auto& pair : effects) {
        result += "\"" + pair.first + "\": " + std::to_string(pair.second) + ", ";
    }
    result += "};";
    return result;
}

std::ostream& operator<<(std::ostream& os, const Descriptor& obj) {
    os << obj.toString();
    return os;
}