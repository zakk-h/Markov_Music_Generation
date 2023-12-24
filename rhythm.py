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

#Cases for the matrix
#A triplet may only start on the beat (x.0), with the exception of 8th note triplets which can also start on the ands (x.5).
#From any non-triplet, the chain has 0 probability of transitioning to note 2 or note 3 of a triplet. It can only transition to note 1 of a triplet.
#From triplet note 1, it must go to triplet note 2, and then go to triplet note 3. This can be any combination of rests or non-rests.
#In the future, triplets could be able to go to other types of triplets while maintaining the original structure of the triplet, but that is too difficult right now.
#The chance of moving or starting at a dotted sixteenth should be 0 (too hard).

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

def is_valid_triplet_transition(current_state, next_state):

    if ("Triplet" not in next_state) and "Triplet 3" in current_state:
        return True
    if ("Triplet" not in next_state) and "Triplet" in current_state: 
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
        return round(next_triplet_num,3) == current_triplet_num + 1

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
    next_beat = float(next_state.split(" Beat ")[1])
    next_note_type = next_state.split(" ")[0]

    # Calculate the duration of the next note type
    duration = calculate_duration(next_state)
    
    #print(f"next beat {next_beat}")
    #print(f"duration {duration}")
    #print((round(next_beat + duration,3) <= time_signature[0] + 1))

    # Check if the addition would fit in the measure. If it doesn't, it should be an invalid next note. In 4/4, this would stop dotted whole notes.
    return (round(next_beat + duration,3) <= time_signature[0] + 1)



num_states = len(states)
transition_matrix = np.ones((num_states, num_states))  # Initialize with ones

# Setting probabilities
for i, current_state in enumerate(states):
    for j, next_state in enumerate(states):
        

        if "Dotted Sixteenth" in next_state: #Could include current state, but if that somehow happens it should go somewhere.
            transition_matrix[i][j] = 0
            continue
        if "Triplet" in current_state:
            if is_valid_triplet_transition(current_state, next_state):
                transition_matrix[i][j] = 1  # or other probability as needed, normalize later
            else:
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
        if not is_regular_transition_allowed(current_state, next_state):
            transition_matrix[i][j] = 0

# Normalize the matrix
for i in range(num_states):
    row_sum = sum(transition_matrix[i])
    if row_sum > 0:
        transition_matrix[i] /= row_sum

print("Transition Matrix:\n", transition_matrix)

def generate_n_notes(length=10):
    rhythm = []
    current_beat = 1  # Start at Beat 1

    # Filter for states at Beat 1 that are either quarter or eighth notes
    possible_start_states = [state for state in states 
                             if round(float(state.split(" Beat ")[1]), 3) == 1.0 and
                             ("Quarter" in state or "Eighth" in state) and
                             "Triplet" not in state and 
                             "Dotted Eighth" not in state]

    if not possible_start_states:
        print("Error: No starting states at Beat 1 that meet starting criteria")
        return []

    current_state = np.random.choice(possible_start_states)
    current_state_index = states.index(current_state)
    rhythm.append(current_state)

    # Update the current beat based on the chosen starting state
    current_beat += calculate_duration(current_state)

    for _ in range(1, length):
        # Wrap the current beat if it exceeds the time signature
        if current_beat > time_signature[0]:
            current_beat = (current_beat - 1) % time_signature[0] + 1

        # Filter states based on the current beat
        possible_states_indices = [i for i, state in enumerate(states)
                                   if round(float(state.split(" Beat ")[1]), 3) == round(current_beat, 3)]

        if not possible_states_indices:
            print("Error/End: No valid states to choose from")
            break

        # Calculate the sum of probabilities for the filtered states
        probabilities = [transition_matrix[current_state_index][i] for i in possible_states_indices]
        probabilities_sum = sum(probabilities)

        if probabilities_sum == 0:
            print("Error/End: No valid transition")
            break

        # Normalize probabilities for the filtered states
        normalized_probabilities = [p / probabilities_sum for p in probabilities]

        # Choose the next state index from the filtered states based on normalized probabilities
        current_state_index = np.random.choice(possible_states_indices, p=normalized_probabilities)
        current_state = states[current_state_index]
        
        rhythm.append(current_state)

        # Update the current beat based on the duration of the new current state
        current_beat += calculate_duration(current_state)
        # Print states with positive probability for the next transition
        
        #print("Current State:", current_state)
        #print("Possible next states with their probabilities:")
        
        for idx, probability in enumerate(transition_matrix[current_state_index]):
            state_beat = round(float(states[idx].split(" Beat ")[1]), 3)
            if probability > 0 and state_beat == round(current_beat, 3):
                print(f"    {states[idx]}: {probability}")
            

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


def rhythm_to_lilypond(rhythm):
    lilypond_notes = []
    current_beat = 0.0

    for r in rhythm:
        note_type, beat_info = r.split(" Beat ")
        duration = note_type.split()[0]

        # Calculate the note duration in LilyPond format
        if duration == "Whole":
            lily_duration = "1"
        elif duration == "Half":
            lily_duration = "2"
        elif duration == "Quarter":
            lily_duration = "4"
        elif duration == "Eighth":
            lily_duration = "8"
        elif duration == "Sixteenth":
            lily_duration = "16"
        elif duration == "Dotted Half":
            lily_duration = "2."
        elif duration == "Dotted Quarter":
            lily_duration = "4."
        elif duration == "Dotted Eighth":
            lily_duration = "8."
        elif duration == "Dotted Sixteenth":
            lily_duration = "16."
        else:
            lily_duration = "4"  # Default to quarter note

        # Identify if the current element is a note or a rest
        is_rest = "Rest" in note_type

        # Handle triplets
        if "Triplet" in note_type:
            if "1" in note_type:  # Start of triplet
                lilypond_notes.append(f"\\tuplet 3/2 {{ c{'' if not is_rest else ','}{lily_duration}")
            elif "2" in note_type:  # Middle of triplet
                lilypond_notes.append(f"c{'' if not is_rest else ','}{lily_duration}")
            elif "3" in note_type:  # End of triplet
                lilypond_notes.append(f"c{'' if not is_rest else ','}{lily_duration} }}")
        else:
            # Append note or rest to the lilypond list
            if is_rest:
                lilypond_notes.append(f"r{lily_duration}")
            else:
                lilypond_notes.append(f"c'{lily_duration}")

    return " ".join(lilypond_notes)


lilypond_string = rhythm_to_lilypond(sample_rhythm)

# This will produce a string like "c'4 c,8 c'4" that you can then embed into a LilyPond script
print(lilypond_string)

import subprocess
import os
from PIL import Image

def display_music_lilypond(lilypond_string):
    # Create a full LilyPond script
    script = f"""
    \\version "2.20.0"
    \\score {{
        \\new Staff {{
            \\time 4/4
            {lilypond_string}
        }}
        \\layout {{ }}
        \\midi {{ }}
    }}
    """

    # Write the script to a temporary file
    with open("temp.ly", "w") as file:
        file.write(script)

    # Call LilyPond to compile the file
    subprocess.run(["lilypond", "--png", "temp.ly"])

    # Open and display the generated PNG file
    img = Image.open("temp.png")
    img.show()

# Example usage
display_music_lilypond(lilypond_string)

print(is_regular_transition_allowed('Dotted Eighth Beat 2.5', 'Dotted Half Beat 3.2500000000000013'))