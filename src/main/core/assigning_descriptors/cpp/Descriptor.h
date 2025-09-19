#ifndef DESCRIPTOR_H
#define DESCRIPTOR_H

#include <string>
using std::string;
#include <map>
using std::map;
#include <iostream>

class Descriptor {
private:
    string name;
    map<string, float> effects;
    bool fixed;
public:
    Descriptor(string name, map<string, float> effects = {}, bool fixed = false);
    string getName() const;
    map<string, float> getEffects() const;
    float getEffect(string demographic) const;
    float setEffect(string demographic, float effect);
    float addEffect(string demographic, float effect);
    bool isFixed() const;
    bool operator==(const Descriptor& other) const;
    string toString() const;
    friend std::ostream& operator<<(std::ostream& os, const Descriptor& obj);
};

#endif