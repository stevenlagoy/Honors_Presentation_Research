from typing import Dict, List, Any
from math import sqrt, log2
from random import randint, choice, random

from MapEntity import MapEntity, Nation, State, states, County, counties
from Descriptor import Descriptor, descriptors, DESCRIPTORS_MAX
# from Demographic import Demographic

temperature = 0.05 # How likely a change is to be accepted which decreases score

def normalize(vec: List[float]) -> List[float]:
    s = sum(vec)
    if s == 0:
        return [0 for _ in vec]
    return [x/s for x in vec]

def initialize():
    global descriptors_count
    # Create base descriptors: one for nation, one for each state
    Nation.get_instance().descriptors.append(Descriptor("nation", {}, True))
    for state in states:
        state.descriptors.append(Descriptor(state.name.lower().replace(" ","_"), {}, True))
    # Initialize all other descriptors
    for i in range(DESCRIPTORS_MAX):
        descriptors.add(Descriptor(f"Descriptor {i}", {}))

# favor descriptors which reflect real life - Accuracy
accuracy = 2.0 # Accuracy of 2x is 1 plus this many times better than Accuracy of 1x
# favor fewer number of descriptors - Parsimony
parsimony = 1.5 # Descriptor Count of 1x is this many times better than Count of 2x
# favor descriptors with greater effects - Specificity
specificity = 1.125 # Descriptor with a 10x effect on 1x demographics is this many times better than Descriptor with 1x effect on 10x demographics 

sums = sum([accuracy, parsimony, specificity])
accuracy /= sums
parsimony /= sums
specificity /= sums
def score():

    score = 0

    # Score Map Entities for Accuracy

    # nation_score = 0
    # nation = Nation.get_instance()
    # nation_score += compare_demographics(nation.demographics, nation.descriptor_demographics())

    # states_scores = 0
    # for state in states:
    #     states_scores += compare_demographics(state.demographics, state.descriptor_demographics())
    # states_scores /= len(states)
    
    # counties_scores = 0
    # for county in counties:
    #     counties_scores += compare_demographics(county.demographics, county.descriptor_demographics())
    # counties_scores /= len(counties)

    # accuracy_score = (nation_score + states_scores + counties_scores) / 3

    ''' Because the state and nation demographics are reflected in county demographic accuracy, we only need to calculate at the county level. '''

    accuracy_score = score_counties_accuracies()

    # Score Descriptors for Parsimony and Specificity

    # active_descriptors = 0
    # for descriptor in descriptors:
    #     for effect in descriptor.effects:
    #         if descriptor.effects[effect] != 0:
    #             active_descriptors += 1
    # parsimony_score = active_descriptors / DESCRIPTORS_MAX

    # specificity_score = 0
    # for descriptor in descriptors:
    #     count_effects = len(descriptor.effects)
    #     if count_effects == 0:
    #         continue
    #     total_effects = sum(descriptor.effects.values())
    #     average_effect = total_effects / count_effects
    #     specificity_score += average_effect
    # specificity_score /= max(active_descriptors, 1)
    
    # # print(f"{accuracy_score=} {parsimony_score=} {specificity_score=}")
    # score = accuracy_score * accuracy + parsimony_score * parsimony + specificity_score * specificity
    # print(f"{score=}")

    score = accuracy_score
    return score

def score_nation_accuracy() -> float:
    ''' Scores the nation and returns accuracy. '''
    nation = Nation.get_instance()
    return compare_demographics(nation.demographics, nation.descriptor_demographics())

def score_states_accuracies() -> float:
    ''' Scores all states and returns the average accuracy. '''
    score = 0
    for state in states:
        score += compare_demographics(state.normalized_demographics, state.descriptor_demographics())
    score /= len(states)
    return score

def compare_demographics(expected: Dict[Any, float], actual: Dict[Any, float], method: str = "js") -> float:
    ''' Compare expected and actual demographic distributions. Returns a similarity score
        (1 = identical, 0.5 = somewhat different, 0 = most different).
        Methods (which method of comparison to use):
            "l1"        sum abs differences
            "l2"        eucledian norm
            "cosine"    cosine similarity or angle of vectors
            "js"        Jensen-Shannon divergence
    '''
    
    # Dicts are already normalized by MapEntity.normalized_demographics
    # Normalize union of keys
    keys = set(expected) | set(actual)
    e = [expected.get(k, 0.0) for k in keys]
    a = [actual.get(k, 0.0) for k in keys]

    e = normalize(e)
    a = normalize(a)
    
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
        def kl(p, q): # KL-divergence function NOTE: Asymmetric- KL(P,Q) != KL(Q,P)
            return sum(
                p[i] * log2(p[i]/q[i])
                for i in range(len(p))
                if p[i] > 0 and q[i] > 0
            )
        # calculate J-S Divergence
        m = [(x+y)/2 for x, y in zip(e, a)]
        js = (kl(e, m) + kl(a, m)) / 2
        sim = 1 - js # Invert
        return max(0.0, min(1.0, sim)) # Clamp to [0, 1]

    raise ValueError(f"Unknown method: {method}")

county_scores = {county: compare_demographics(county.normalized_demographics, county.descriptor_demographics()) for county in counties}
def score_counties_accuracies() -> float:
    ''' Scores all counties and returns the average accuracy. '''
    return sum(county_scores.values()) / len(county_scores)

class Change:
    def __init__(self, undo_fn):
        self.undo_fn = undo_fn
    def undo(self):
        self.undo_fn()

def permute() -> Change:
    # Pick randomly an entity to add / remove descriptor, or a descriptor to add / remove / change effect
    if randint(0,1): # Add or remove descriptor from a county or state
        # Pick a county or state
        entity: MapEntity = choice(counties + states)
        # Choose whether to add or remove descriptor
        if randint(0,1): # Add
            # Choose a descriptor to add
            descriptor: Descriptor = choice(list(descriptors))
            if descriptor.fixed:
                return permute() # Cannot change the descriptor: try again
            # Add it to the entity's descriptors
            entity.descriptors.append(descriptor)
            def undo():
                entity.descriptors.remove(descriptor)
                if isinstance(entity, County):
                    county_scores[entity] = compare_demographics(entity.normalized_demographics, entity.descriptor_demographics(), "l1")
            # Update the cache
            if isinstance(entity, County):
                county_scores[entity] = compare_demographics(entity.normalized_demographics, entity.descriptor_demographics(), "l1")
            return Change(undo)
        else: # Remove
            if len(entity.descriptors) == 0:
                return permute() # Nothing to remove: try again
            # Choose a descriptor to remove
            descriptor: Descriptor = choice(entity.descriptors)
            if descriptor.fixed:
                return permute() # Cannot change the descriptor: try again
            # Remove it from the entity's descriptors
            entity.descriptors.remove(descriptor)
            def undo():
                entity.descriptors.append(descriptor)
                if isinstance(entity, County):
                    county_scores[entity] = compare_demographics(entity.normalized_demographics, entity.descriptor_demographics(), "l1")
            # Update the cache
            if isinstance(entity, County):
                county_scores[entity] = compare_demographics(entity.normalized_demographics, entity.descriptor_demographics(), "l1")
            return Change(undo)
    else: # Add, remove, or change a descriptor's effect
        # Pick a descriptor
        descriptor: Descriptor = choice(list(descriptors))
        # Choose an effect to change
        effect: str = choice([_ for _ in descriptor.effects.keys()])
        # Determine how much to change by
        change = 0.001 if randint(0,1) else -0.001
        old_value = descriptor.effects[effect]
        descriptor.effects[effect] += change
        # Refresh any county using this descriptor
        affected = [c for c in counties if descriptor in c.descriptors]
        for c in affected:
            county_scores[c] = compare_demographics(c.normalized_demographics, c.descriptor_demographics(), "l1")
        def undo():
            descriptor.effects[effect] = old_value
            for c in affected:
                county_scores[c] = compare_demographics(c.normalized_demographics, c.descriptor_demographics(), "l1")
        return Change(undo)

prev_score = 0
def run():

    prev_score = score()

    while True:
        change = permute()
        new_score = score()
        print(f"{new_score}")
        if new_score - prev_score < 0 and random() > temperature:
            # Restore previous state
            change.undo()
        else:
            # Accept the change
            prev_score = new_score

def main() -> None:

    initialize()

    try:
        run()
    except KeyboardInterrupt:
        with open("logs\\log.out",'w',encoding='utf-8') as out:
            out.write(str(Nation.get_instance()) + "\n")
            for state in states:
                out.write(str(state) + "\n")
            for county in counties:
                out.write(str(county) + "\n")
            for descriptor in descriptors:
                out.write(str(descriptor) + "\n")

if __name__ == "__main__":
    main()