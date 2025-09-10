from typing import List, Dict
import numpy as np
from random import choice, random

from County import County, counties
from Descriptor import Descriptor, descriptors

def initialize():
    # Assign base descriptors to each county
    nation = Descriptor("Nation", fixed=True)
    for county in counties:
        county.descriptors.append(nation)
        county.descriptors.append(Descriptor(county.state, fixed=True))
        score_county(county)

def normalize(vec: List[float]) -> List[float]:
    ''' Normalize a positive vector of any length. '''
    s = sum(vec)
    if s == 0:
        return [0 for _ in vec]
    return [x/s for x in vec]

def compare_demographics(expected: Dict[str, float], actual: Dict[str, float], method: str = "l1") -> float:

    keys = set(expected) | set(actual)
    e = [expected.get(k, 0.0) for k in keys]
    a = [actual.get(k, 0.0) for k in keys]
    e = normalize(e)
    a = normalize(a)

    if method == "l1": # L1 Norm - Sum of absolute differences (Manhattan Distance)
        dist = sum(abs(x - y) for x, y in zip(e, a))
        return 1 - dist / 2 # Normalize to [0, 1]
        
    if method == "l2": #  L2 Norm - Euclidian distance
        dist = np.sqrt(sum((x - y) ** 2 for x, y in zip(e, a))) # Euclidian norm: √(Σ{i=1,n}(|x_i|^2)) : x_i = expected_i - actual_i
        return 1 - dist / 2 # normalize to [0, 1]

    if method == "cosine": # Cosine similarities
        # Both vectors are normalized, so cosine similarity is just the dot product
        return np.dot(np.array(e), np.array(a))

    if method == "js": # Jensen-Shannon Divergence
        def kl(p, q): # KL-divergence function NOTE: Asymmetric- KL(P,Q) != KL(Q,P)
            return sum(
                p[i] * np.log2(p[i]/q[i])
                for i in range(len(p))
                if p[i] > 0 and q[i] > 0
            )
        # calculate J-S Divergence
        m = [(x+y)/2 for x, y in zip(e, a)]
        js = (kl(e, m) + kl(a, m)) / 2
        sim = 1 - js # Invert
        return max(0.0, min(1.0, sim)) # Clamp to [0, 1]

    raise ValueError(f"Unknown method: {method}")

class Change:
    def __init__(self, undo_fn):
        self.undo_fn = undo_fn
    def undo(self):
        self.undo_fn()

# Maximum amount which a descriptor could have an effect changed by in one permutation
MAX_PERMUTE_CHANGE = 0.1
def permute_descriptors() -> Change | None:
    if len(descriptors) == 0:
        return None
    # Select a descriptor to modify
    descriptor = choice(list(descriptors))
    # Select an effect in the descriptor to modify
    effect = choice([k for k in descriptor.effects.keys()])
    # Choose how much to modify
    mod = random() * MAX_PERMUTE_CHANGE
    old_value = descriptor.effects[effect]
    descriptor.effects[effect] = min(1.0, max(0.0, old_value + mod)) # Clamp to [0.0, 1.0]
    for county in counties:
        if descriptor in county.descriptors:
            score_county(county)
    def undo():
        descriptor.effects[effect] = old_value
        for county in counties:
            if descriptor in county.descriptors:
                score_county(county)
    return Change(undo)

counties_scores = {county: 0.0 for county in counties}    
def score_county(county: County) -> float:
    counties_scores[county] = compare_demographics(county.demographics, county.descriptor_demographics(), "l1")
    return counties_scores[county]

def score() -> float:
    return sum([v for v in counties_scores.values()]) / len(counties_scores)

def run():
    while True:
        permute_descriptors()
        print(score())

def write_output():
    with open("logs\\log.out",'w',encoding='utf-8') as out:
        for county in counties:
            out.write(str(county) + "\n")
        for descriptor in descriptors:
            out.write(str(descriptor) + "\n")

def main() -> None:
    try:
        initialize()
        run()
    except KeyboardInterrupt:
        write_output()

if __name__ == "__main__":
    main()