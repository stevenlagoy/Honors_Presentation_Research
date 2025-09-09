from typing import Dict, List, Any
from math import sqrt, log2

from MapEntity import Nation, State, states, County, counties
from Descriptor import Descriptor, descriptors
from Demographic import Demographic

def initialize():
    Nation.get_instance().descriptors.append(Descriptor("nation", {}, False))
    for state in states:
        state.descriptors.append(Descriptor(state.name.lower().replace(" ","_"), {}, False))

def randomize():
    ...

def score():
    # favor descriptors which reflect real life - Accuracy
    accuracy = 1.0 # Accuracy of 2x is 1 plus this many times better than Accuracy of 1x
    # favor fewer number of descriptors - Parsimony
    parsimony = 1.5 # Descriptor Count of 1x is this many times better than Count of 2x
    # favor descriptors with greater effects - Specificity
    specificity = 1.125 # Descriptor with a 10x effect on 1x demographics is this many times better than Descriptor with 1x effect on 10x demographics 
    
    score = 0

    nation = Nation.get_instance()

    states_scores = 0
    for state in states:
        states_scores += compare_demographics(state.demographics, state.descriptor_demographics())
    states_scores /= len(states)
    
    counties_scores = 0
    for county in counties:
        counties_scores += compare_demographics(county.demographics, county.descriptor_demographics())
    counties_scores /= len(counties)

    for descriptor in descriptors:
        ...
    
    print(f"{states_scores=}, {counties_scores=}")

def compare_demographics(expected: Dict[Any, float], actual: Dict[Any, float], method: str = "js") -> float:
    ''' Compare expected and actual demographic distributions. Returns a similarity score
        (1 = identical, 0.5 = somewhat different, 0 = most different). Methods (which method of
        comparison to use): "l1" sum abs differences, "l2" eucledian norm, "cosine" cosine
        similarity or angle of vectors, "js" Jensen-Shannon divergence. '''
    
    # Normalize keys
    keys = set([expected[k] for k in expected]) | set([actual[k] for k in actual])
    e = []
    for k in keys:
        v = expected.get(k, 0.0)
        e.append(v)
    #e = [expected.get(k, 0.0) for k in keys]
    a = [actual.get(k, 0.0) for k in keys]
    
    if method == "l1": # Sum of absolute differences
        dist = sum(abs(x - y) for x, y in zip(e, a)) # Sum of absolute differences Σ{i=1,n}(|x_i|) : x_i = expected_i - actual_i
        return 1 - dist / 2 # normalize to [0, 1]
    
    if method == "l2": # Eucledian norm
        dist = sqrt(sum((x - y) ** 2 for x, y in zip(e, a))) # Eucledian norm: √(Σ{i=1,n}(|x_i|^2)) : x_i = expected_i - actual_i
        return 1 - dist / 2 # normalize to [0, 1]

    if method == "cosine": # Cosine similarity
        dot = sum(x*y for x, y in zip(e, a)) # e ⋅ a = Σ{i}(e_i*a_i)
        norm_e = sqrt(sum(x*x for x in e)) # ||e|| = √(Σ{i}(e_i^2))
        norm_a = sqrt(sum(y*y for y in a)) # ||a|| = √(Σ{i}(a_i^2))
        return dot / (norm_e * norm_a + 1e-12) # Cosine similarity. Add small value to avoid division by zero

    if method == "js": # Jensen-Shannon Divergence
        def kl(p, q): # KL-divergence function NOTE: Asymmetric KL(P,Q) != KL(Q,P)
            return sum(p[i] * log2(p[i]/q[i]) for i in range(len(p)) if p[i] > 0 and q[i] > 0)
        m = [(x+y)/2 for x, y in zip(e, a)]
        js = (kl(e, m) + kl(a, m)) / 2
        return 1 - js # Invert

    raise ValueError(f"Unknown method: {method}")

def permute():
    ...

def main() -> None:
    initialize()
    score()

if __name__ == "__main__":
    main()