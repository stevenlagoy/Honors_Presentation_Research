#include <map>
#include <string>
#include <set>
#include <array>
#include <vector>
#include <numeric>
#include <algorithm>
#include <stdexcept>
#include <cstdlib>
#include <cmath>
#include <iostream>
#include <windows.h>
#include <fstream>
#include "../../../../lib/json.hpp"
using json = nlohmann::json;
#include <sstream>
#include <random>
#include <iterator>

#include "Descriptor.h"
#include "County.h"

using namespace std;

#define MAX_DESCRIPTORS 300
#define MAX_PERMUTE_CHANCE 0.1f

void normalize(vector<float>& vec) {
    float sum = accumulate(vec.begin(), vec.end(), 0);
    if (sum == 0.0) return;
    for (auto it = vec.begin(); it != vec.end(); ++it) {
        *it /= sum;
    }
}

float compareDemographics(map<string, float> expected, map<string, float> actual, string method = "l1") {

    // Create normalized vectors with zipped values
    // Get all keys from both maps
    set<string> keys = set<string>();
    for (const auto& pair : expected) {
        keys.insert(pair.first);
    }
    for (const auto& pair : actual) {
        keys.insert(pair.first);
    }
    // Create mutually-regular vectors
    vector<float> e, a;
    for (const string& key : keys) {
        auto e_it = expected.find(key);
        e.emplace_back(e_it == expected.end() ? 0.0 : e_it->second);
        auto a_it = actual.find(key);
        a.emplace_back(a_it == actual.end() ? 0.0 : a_it->second);
    }
    // Normalize vectors
    normalize(e);
    normalize(a);

    // Check if population disparity
    if (accumulate(a.begin(), a.end(), 0) == 0.0 &&
        accumulate(e.begin(), e.end(), 0) != 0.0) {
        return 0.0;
    }

    if (method == "l1") { // L1 Norm - Sum of absolute differences (Manhattan Distance)
        vector<float> distances = vector<float>();
        for (size_t i = 0; i < e.size(); i++) {
            distances.emplace_back(abs(e.at(i) - a.at(i)));
        }
        float dist = accumulate(distances.begin(), distances.end(), 0.0);
        return 1 - dist / 2; // Normalize to [0, 1]
    }
    else if (method == "l2") { // L2 Norm - Eucledian distance
        vector<float> distances = vector<float>();
        for (size_t i = 0; i < e.size(); i++) {
            distances.emplace_back(pow(e.at(i) - a.at(i), 2));
        }
        float dist = sqrt(accumulate(distances.begin(), distances.end(), 0.0));
        return 1 - dist / 2; // Normalize to [0, 1]
    }
    else if (method == "cosine") { // Cosine Similarities - Dot product
        float dot = inner_product(e.begin(), e.end(), a.begin(), 0.0);
        return dot;
    }
    else if (method == "js") { // Jensen-Shannon Divergence
        auto kl = [](vector<float> p, vector<float> q) { // Kullback-Leibler
            vector<float> d = vector<float>();
            for(size_t i = 0; i < p.size(); ++i) {
                if (p[i] && q[i])
                    d.emplace_back(p[i] * log2(p[i]/q[i]));
            }
            float sum = accumulate(d.begin(), d.end(), 0.0);
            return sum;
        };
        vector<float> m = vector<float>();
        for (size_t i = 0; i < e.size(); ++i) {
            m.emplace_back((e.at(i) + a.at(i))/2);
        }
        float js = (kl(e, m) + kl(a, m)) / 2; // Get J-S divergence
        float sim = 1 - js; // Invert
        return clamp(sim, 0.0f, 1.0f);
    }
    else { // Invalid method
        throw invalid_argument("Unknown method: " + method);
    }
}

unordered_map<County*, float> countiesScores;
float scoreCounty(County& c) {
    float score = compareDemographics(c.getDemographics(), c.descriptorDemographics());
    countiesScores[&c] = score;
    return score;
}

float score() {
    size_t num = countiesScores.size();
    if (num == 0) return 0.0f;
    float avgScore = 0.0f;
    for (const auto& s : countiesScores) {
        avgScore += s.second / num;
    }
    return avgScore;
}

vector<string> listDirectories(const string& path) {
    vector<string> dirs;
    WIN32_FIND_DATAA fd;
    HANDLE hFind = FindFirstFileA((path + "\\*").c_str(), &fd);

    
    if (hFind == INVALID_HANDLE_VALUE) return dirs;
    
    do {
        string name = fd.cFileName;
        if ((fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) && name != "." && name != "..") {
            dirs.push_back(name);
        }
    } while (FindNextFileA(hFind, &fd));

    FindClose(hFind);
    return dirs;
}

vector<string> listFiles(const string& path) {
    vector<string> files;
    WIN32_FIND_DATAA fd;
    HANDLE hFind = FindFirstFileA((path + "\\*").c_str(), &fd);

    if (hFind == INVALID_HANDLE_VALUE) return files;

    do {
        string name = fd.cFileName;
        if (!(fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)) {
            files.push_back(name);
        }
    } while (FindNextFileA(hFind, &fd));

    FindClose(hFind);
    return files;
}

void flattenJson(const json& j, map<string, float>& result, const string& parentKey = "", const string& sep = "->") {
    for (auto& [k, v] : j.items()) {
        string newKey = parentKey.empty() ? k : parentKey + sep + k;

        if (v.is_object()) {
            flattenJson(v, result, newKey, sep); // Recurse for nesting
        }
        else if (v.is_number_float() || v.is_number_integer()) {
            result[newKey] = v.get<float>();
        }
        else {
            throw runtime_error("Unsupported type for key " + newKey);
        }

    }
}

// https://stackoverflow.com/a/16421677
template<typename Iter, typename RandomGenerator>
Iter select_randomly(Iter start, Iter end, RandomGenerator& g) {
    uniform_int_distribution<> dis(0, distance(start, end) - 1);
    advance(start, dis(g));
    return start;
}

template<typename Iter>
Iter select_randomly(Iter start, Iter end) {
    static random_device rd;
    static mt19937 gen(rd());
    return select_randomly(start, end, gen);
}

vector<County> counties;

void readCounties() {
    counties.clear();

    for (const string& state : listDirectories("..\\..\\..\\resources")) {
        string countyDir = "..\\..\\..\\resources\\" + state + "\\counties";
        for (const string& file : listFiles(countyDir)) {
            size_t dot = file.find('.');
            if (dot != string::npos && all_of(file.begin(), file.begin() + dot, ::isdigit)) {
                // Open file
                ifstream f(countyDir + "\\" + file);
                if (!f.is_open()) continue;
                
                // Read into buffer
                stringstream buffer;
                buffer << f.rdbuf();
                f.close();
                
                // Read JSON
                json j = json::parse(buffer.str());
                map<string, float> demos;
                flattenJson(j["demographics"], demos);

                // cout << j["FIPS"].get<string>() << endl;

                counties.emplace_back(
                    j["name"].get<string>(),
                    j["state"].get<string>(),
                    j["population"].get<int>(),
                    demos
                );
            }
        }
    }
}

vector<Descriptor> descriptors;
vector<Descriptor> modifiable;

void initialize() {

    // Create counties
    readCounties();

    // Assign base descriptors (nation, state) to each county
    Descriptor nation("Nation", {}, true);
    descriptors.emplace_back(nation);
    map<string, Descriptor> states;
    for (County& c : counties) {
        c.addDescriptor(nation);
        if (states.count(c.getState()) == 0) {
            Descriptor d(c.getState(), {}, true);
            descriptors.emplace_back(d);
            states.insert({ c.getState(), d });
        }
        c.addDescriptor(states.at(c.getState()));
    }

    // Create blank descriptors up to MAX_DESCRIPTORS
    for (int i = 0; descriptors.size() <= MAX_DESCRIPTORS; ++i) {
        Descriptor d("Descriptor " + to_string(i));
        descriptors.emplace_back(d);
        modifiable.emplace_back(d);
    }
}

struct Change {
    function<void()> undo_fn;
    Change(function<void()> fn) : undo_fn(fn) {}
    void undo() { if (undo_fn) undo_fn(); }
};

Change permuteDescriptors() {
    if (descriptors.empty()) {
        return Change([](){});
    }
    // Select a descriptor to modify
    Descriptor* descriptor = &*select_randomly(descriptors.begin(), descriptors.end());
    // Select an effect in the descriptor to modify
    map<string, float> effects = descriptor->getEffects();
    if (effects.empty()) {
        return Change([](){});
    }
    auto& effect = *select_randomly(effects.begin(), effects.end());
    const string key = effect.first;
    float old_value = effect.second;
    // Choose how much to modify
    float mod = static_cast<float>(rand()) / static_cast<float>(RAND_MAX/MAX_PERMUTE_CHANCE) - MAX_PERMUTE_CHANCE / 2.0f; // value in range [-MAX_PERMUTE_CHANCE, MAX_PERMUTE_CHANCE]
    float new_value = clamp(old_value + mod, 0.0f, 1.0f);
    descriptor->setEffect(key, new_value);
    // Recalculate scores
    vector<County*> affected;
    for (auto& c : counties) {
        if (c.hasDescriptor(*descriptor)) {
            c.recalculate();
            scoreCounty(c);
            affected.push_back(&c);
        }
    }
    return Change([descriptor, key, old_value, affected]() mutable {
        descriptor->setEffect(key, old_value);
        for (auto* c : affected) {
            c->recalculate();
            scoreCounty(*c);
        }
    });
}

Change permuteCounties() {
    if (counties.empty() || descriptors.empty()) {
        return Change([](){});
    }
    // Select a county to modify
    County* county = &*select_randomly(counties.begin(), counties.end());
    // Select a modifiable descriptor
    Descriptor* descriptor = &*select_randomly(modifiable.begin(), modifiable.end());
    // Determine whether to add or remove
    bool had_descriptor = county->hasDescriptor(*descriptor);
    if (had_descriptor) {
        county->removeDescriptor(*descriptor);
    }
    else {
        county->addDescriptor(*descriptor);
    }
    county->recalculate();
    scoreCounty(*county);

    return Change([county, descriptor, had_descriptor]() mutable {
        if (had_descriptor) {
            county->addDescriptor(*descriptor);
        }
        else {
            county->removeDescriptor(*descriptor);
        }
        county->recalculate();
        scoreCounty(*county);
    });
}

void run() {
    float prev_score = 0, new_score;
    Change change([](){});
    while (true) {
        change = permuteDescriptors();
        new_score = score();
        if (prev_score > new_score) {
            change.undo();
        }
        else {
            prev_score = new_score;
            cout << new_score << endl;
        }

        change = permuteCounties();
        new_score = score();
        if (prev_score > new_score) {
            change.undo();
        }
        else {
            prev_score = new_score;
            cout << new_score << endl;
        }
    }
}

int main() {

    initialize();
    run();

    for (const auto& c : counties) {
        cout << c << endl;
    }
    for (const auto& d : descriptors) {
        cout << d << endl;
    }

    return 0;
}