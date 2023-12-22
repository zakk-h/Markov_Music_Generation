# Rhythmic elements
rhythmic_elements = ["Whole", "Half", "Quarter", "Eighth", "Sixteenth", "Dotted Whole", "Dotted Half", "Dotted Quarter", "Dotted Eighth", "Dotted Sixteenth", "Whole Triplet 1", "Whole Triplet 2", "Whole Triplet 3", "Half Triplet 1", "Half Triplet 2", "Half Triplet 3", "Quarter Triplet 1", "Quarter Triplet 2", "Quarter Triplet 3", "Eighth Triplet 1", "Eighth Triplet 2", "Eighth Triplet 3", "Whole Rest", "Half Rest", "Quarter Rest", "Eighth Rest", "Sixteenth Rest", "Dotted Whole Rest", "Dotted Half Rest", "Dotted Quarter Rest", "Dotted Eighth Rest", "Dotted Sixteenth Rest", "Whole Triplet 1 Rest", "Whole Triplet 2 Rest", "Whole Triplet 3 Rest", "Half Triplet 1 Rest", "Half Triplet 2 Rest", "Half Triplet 3 Rest", "Quarter Triplet 1 Rest", "Quarter Triplet 2 Rest", "Quarter Triplet 3 Rest", "Eighth Triplet 1 Rest", "Eighth Triplet 2 Rest", "Eighth Triplet 3 Rest"     ]
#This base set of values can build the duration of any note. If "Dotted Whole", the product of "Whole" and "Dotted". If Half Note Triplet, my convention is half note means the triplet spans the half note, and 2*1/3 gives that value.
rhythmic_values = {
        "Whole": 4, "Half": 2, "Quarter": 1, "Eighth": 1/2, "Sixteenth": 1/4, "Triplet": 1/3, "Dotted": 1.5
    }
#Each of these values should be multiplied by the GCD to be used. 

# States considering the beat position
states = []
time_signature = [4, 4]
#What interval is a divisor of both duple and triple time? If both 8th note triplets (3 notes lasting 1/2 beat total) and 16th notes (2 notes lasting 1/2 beat total), what is the minimum speed would I have to play for each to fall on one of my strokes?
#This would be 6 notes per 1/2 beat or 12 notes per beat.
gcd = 1/12  # Step for the loop
beat = 1  # Initialize beat

while beat < time_signature[0]+1:
    for element in rhythmic_elements:
        states.append(f"{element} Beat {beat}")
    beat += gcd  # Increment by the smallest value divisible by all rhythmic elements

print("States:", states)

import numpy as np

num_states = len(states)
transition_matrix = np.ones((num_states, num_states))  # Initialize with ones


#Cases for the matrix
#A triplet may only start on the beat (x.0), with the exception of 8th note triplets which can also start on the ands (x.5).
#From any non-triplet, the chain has 0 probability of transitioning to note 2 or note 3 of a triplet. It can only transition to note 1 of a triplet.
#From triplet note 1, it must go to triplet note 2, and then go to triplet note 3. This can be any combination of rests or non-rests.
#In the future, triplets could be able to go to other types of triplets while maintaining the original structure of the triplet, but that is too difficult right now.
#The chance of moving or starting at a dotted sixteenth should be 0 (too hard).

def is_valid_triplet_transition(current_state, next_state):

    if "Triplet" not in next_state and "Triplet 3" in current_state:
        return True
    if "Triplet" not in next_state and "Triplet" in current_state: 
        return False
    
    # Check if both states are part of a triplet sequence
    if not ("Triplet" in current_state and "Triplet" in next_state):
        return False
    
    # Extract the part of the state string that specifies the triplet type
    current_triplet_type = current_state.split(" Triplet")[0]
    next_triplet_type = next_state.split(" Triplet")[0]
    
    if current_triplet_type == next_triplet_type:
        # Extract the triplet number from both states
        current_triplet_num = int(current_state.split("Triplet ")[1].split()[0])
        next_triplet_num = int(next_state.split("Triplet ")[1].split()[0])

        # Check if the next state's triplet number is exactly one more than the current state's
        return next_triplet_num == current_triplet_num + 1

    return False


def is_triplet_start_allowed(current_state):
    # Extract the current beat from the state
    current_beat = float(current_state.split(" Beat ")[1])
    current_note_type = current_state.split(" ")[0]

    # Calculate the duration of the current note type
    duration = rhythmic_values.get(current_note_type, 1)

    # Check if the current beat is a whole number (on the beat)
    if (round(current_beat,3)).is_integer():
        # Check if the triplet would fit in the measure
        if round(current_beat + duration,3) <= time_signature[0] + 1:
            return True

    # Additional check for eighth note triplets starting on the offbeat (x.5)
    elif current_note_type == "Eighth" and (round(current_beat * 2,3)) % 1 == 0:  # Checks if beat is x.5
        if round(current_beat + duration,3) <= time_signature[0] + 1:
            return True

    return False

def is_regular_transition_allowed(current_state, next_state):
    # Implement logic for regular transitions, excluding dotted sixteenth and invalid triplets
    return True

# Setting probabilities
for i, current_state in enumerate(states):
    for j, next_state in enumerate(states):
        if "Triplet" in current_state:
            if is_valid_triplet_transition(current_state, next_state):
                transition_matrix[i][j] = 1  # or other probability as needed, normalize later
            else:
                transition_matrix[i][j] = 0
                continue

        if "Dotted Sixteenth" in next_state: #Could include current state, but if that somehow happens it should go somewhere.
            transition_matrix[i][j] = 0
            continue
        else:
            if "Triplet 1" in next_state:
                if is_triplet_start_allowed(current_state): 
                    transition_matrix[i][j] = 1  # Probability of starting a triplet
                else: 
                    transition_matrix[i][j] = 0 #Cannot start a triplet
                    continue
            if "Triplet 2" in next_state or "Triplet 3" in next_state:
                transition_matrix[i][j] = 0
                continue
            elif is_regular_transition_allowed(current_state, next_state):
                transition_matrix[i][j] = 1  # Regular transition probability, no more cases to check
    

# Normalize the matrix
for i in range(num_states):
    row_sum = sum(transition_matrix[i])
    if row_sum > 0:
        transition_matrix[i] /= row_sum

print("Transition Matrix:\n", transition_matrix)

def calculate_duration(note):
    """
    Calculate the duration of a note.
    """
    duration = 1
    multipliers = []
    for val in rhythmic_values:
        if val in note:
            duration *= rhythmic_values[val]
     

    return duration if duration > 0 else rhythmic_values["Quarter"]  # Default duration

def generate_n_notes(length=5):
    rhythm = []
    current_beat = 1  # Start at Beat 1

    # Filter for states at Beat 1 that are either quarter or eighth notes
    possible_start_states = [state for state in states 
                             if "Beat 1" in state and
                             ("Quarter" in state or "Eighth" in state) and
                             "Triplet" not in state and 
                             "Dotted Eighth" not in state]

    if not possible_start_states:
        print("Error: No starting states at Beat 1 that are quarter or eighth notes")
        return []

    current_state = np.random.choice(possible_start_states)
    current_state_index = states.index(current_state)
    rhythm.append(current_state)

    for _ in range(1, length):
        # Calculate the next beat based on the duration of the current state
        duration = calculate_duration(current_state)
        current_beat += duration
        current_beat = current_beat if current_beat <= time_signature[0] else current_beat % time_signature[0]

        # Choose the next state based on the transition matrix probabilities
        probabilities = transition_matrix[current_state_index]
        next_state_index = np.random.choice(range(num_states), p=probabilities)
        next_state = states[next_state_index]

        # Append the next state to the rhythm and update the current state index
        rhythm.append(next_state)
        current_state_index = next_state_index
        current_state = next_state

        # Reset the current beat if it goes over the time signature limit
        if current_beat > time_signature[0]:
            current_beat -= time_signature[0]

        # Print states with positive probability for the next transition
        '''
        print("Current State:", current_state)
        print("Possible next states with their probabilities:")
        for idx, probability in enumerate(transition_matrix[current_state_index]):
            state_beat = round(float(states[idx].split(" Beat ")[1]), 3)
            if probability > 0 and state_beat == round(current_beat, 3):
                print(f"    {states[idx]}: {probability}")
        '''    

    return rhythm
     

# Normalize the transition matrix
for i in range(num_states):
    row_sum = sum(transition_matrix[i])
    if row_sum > 0:
        transition_matrix[i] = [p / row_sum for p in transition_matrix[i]]
    else:
        # Assign equal probabilities if a row sums to 0
        transition_matrix[i] = [1.0 / num_states for _ in transition_matrix[i]]


# Generate a sample rhythm
sample_rhythm = generate_n_notes()
print("Sample Rhythm:", sample_rhythm)

print(is_valid_triplet_transition("Whole Triplet 1 Rest Beat 2.4166666666666665", "Whole Beat 1.4999999999999996"))