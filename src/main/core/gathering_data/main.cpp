#include <iostream>
#include <vector>
#include <algorithm>

#include "County.h"

int main() {

    std::vector<State> states;
    states.push_back(State("Alabama", 100, std::map<std::string, float>({{"White", 0.5}, {"Hispanic", 0.25}, {"Black", 0.125}, {"Asian", 0.0625}, {"Mixed", 0.03125}, {"Other", 0.03125}})));

    std::vector<County> counties;

    return 0;
}