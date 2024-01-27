import numpy as np
#In Progress: Have the 40 most common transition matrices cached. 2/4 through 5/4 with difficulty levels 1-10 each.

def get_basics(): 
    rhythmic_elements = ["Whole", "Half", "Quarter", "Eighth", "Sixteenth", "Dotted Whole", "Dotted Half", "Dotted Quarter", "Dotted Eighth", "Dotted Sixteenth", "Whole Triplet 1", "Whole Triplet 2", "Whole Triplet 3", "Half Triplet 1", "Half Triplet 2", "Half Triplet 3", "Quarter Triplet 1", "Quarter Triplet 2", "Quarter Triplet 3", "Eighth Triplet 1", "Eighth Triplet 2", "Eighth Triplet 3", "Whole Rest", "Half Rest", "Quarter Rest", "Eighth Rest", "Sixteenth Rest", "Dotted Whole Rest", "Dotted Half Rest", "Dotted Quarter Rest", "Dotted Eighth Rest", "Dotted Sixteenth Rest", "Whole Triplet 1 Rest", "Whole Triplet 2 Rest", "Whole Triplet 3 Rest", "Half Triplet 1 Rest", "Half Triplet 2 Rest", "Half Triplet 3 Rest", "Quarter Triplet 1 Rest", "Quarter Triplet 2 Rest", "Quarter Triplet 3 Rest", "Eighth Triplet 1 Rest", "Eighth Triplet 2 Rest", "Eighth Triplet 3 Rest"     ]
        #This base set of values can build the duration of any note. If "Dotted Whole", the product of "Whole" and "Dotted". If Half Note Triplet, my convention is half note means the triplet spans the half note, and 2*1/3 gives that value.
    rhythmic_values = {
                "Whole": 4, "Half": 2, "Quarter": 1, "Eighth": 1/2, "Sixteenth": 1/4, "Triplet": 1/3, "Dotted": 1.5 }
    return rhythmic_elements, rhythmic_values

rhythmic_elements, rhythmic_values = get_basics()

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

def generate_rhythm_matrix(rhythmic_elements, rhythmic_values, difficulty_level, time_signature): 
    # Rhythmic elements
    #Each of these values should be multiplied by the GCD to be used. 

    # States considering the beat position
    states = []

    #What interval is a divisor of both duple and triple time? If both 8th note triplets (3 notes lasting 1/2 beat total) and 16th notes (2 notes lasting 1/2 beat total), what is the minimum speed would I have to play for each to fall on one of my strokes?
    #This would be 6 notes per 1/2 beat or 12 notes per beat.
    gcd = 1/12  # Step for the loop
    beat = 1  # Initialize beat

    while beat < time_signature[0]+1:
        for element in rhythmic_elements:
            states.append(f"{element} Beat {beat}")
        beat += gcd  # Increment by the smallest value divisible by all rhythmic elements

    print("States:", states)

    #Cases for the matrix
    #A triplet may only start on the beat (x.0), with the exception of 8th note triplets which can also start on the ands (x.5).
    #From any non-triplet, the chain has 0 probability of transitioning to note 2 or note 3 of a triplet. It can only transition to note 1 of a triplet.
    #From triplet note 1, it must go to triplet note 2, and then go to triplet note 3. This can be any combination of rests or non-rests.
    #In the future, triplets could be able to go to other types of triplets while maintaining the original structure of the triplet, but that is too difficult right now.
    #The chance of moving or starting at a dotted sixteenth should be 0 (too hard).

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
            return round(next_triplet_num,3) == round(current_triplet_num + 1,3)

        return False


    def is_triplet_start_allowed(next_state):
        # Split the state to extract the note type and the beat
        note_type, beat_info = next_state.split(" Beat ")
        start_beat = float(beat_info)

        # Determine the duration of the triplet based on its type
        triplet_duration_mapping = {
            "Whole Triplet": 4,    # A whole note triplet spans 4 beats in total
            "Half Triplet": 2,     # A half note triplet spans 2 beats in total
            "Quarter Triplet": 1,  # A quarter note triplet spans 1 beat in total
            "Eighth Triplet": 0.5, # An eighth note triplet spans 0.5 beat in total
        }

        # Extract the base duration type from the note type
        duration_type = " ".join(note_type.split()[:2])  # E.g., "Half Triplet" or "Quarter Triplet"

        # Get the total duration of the triplet
        triplet_duration = triplet_duration_mapping.get(duration_type, 1)  # Default to 1 beat

        # Check if the start beat is on the beat (x.0) or off beat (x.5) for eighth triplets
        is_valid_start_beat = start_beat % 1 == 0 or (duration_type == "Eighth Triplet" and start_beat % 0.5 == 0)

        # Check if the triplet would fit within the measure and if the start beat is valid
        return (start_beat + triplet_duration) <= time_signature[0] + 1 and is_valid_start_beat


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
        return (round(next_beat + duration,3) <= round(time_signature[0] + 1, 3))



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
                    if is_triplet_start_allowed(next_state): 
                        transition_matrix[i][j] = 1  # Probability of starting a triplet
                    else: 
                        transition_matrix[i][j] = 0 #Cannot start a triplet
                        continue
                elif "Triplet 2" in next_state or "Triplet 3" in next_state:
                    transition_matrix[i][j] = 0
                    continue
            if not is_regular_transition_allowed(current_state, next_state):
                transition_matrix[i][j] = 0

    difficulty_divisors = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    difficulty_tiers = [0] + [difficulty_level / divisor for divisor in difficulty_divisors]
    difficulty_divisors = [0] + difficulty_divisors


    #Generating transition matrix.
    for i, current_state in enumerate(states):
        for j, next_state in enumerate(states):
            if transition_matrix[i][j] > 0.01:
                if "Triplet" in next_state: 
                    if "Quarter" in next_state and difficulty_level >= difficulty_divisors[3]:
                        transition_matrix[i][j] = difficulty_tiers[3]   
                    elif "Half" in next_state and difficulty_level >= difficulty_divisors[6]:
                        transition_matrix[i][j] = difficulty_tiers[6]     
                    elif "Whole" in next_state and difficulty_level >= difficulty_divisors[3]:
                        transition_matrix[i][j] = difficulty_tiers[3]  
                    elif "Eighth" in next_state and difficulty_level >= difficulty_divisors[8]:
                        transition_matrix[i][j] = difficulty_divisors[8]
                    else: 
                        transition_matrix[i][j] = 0

                elif "Dotted" in next_state:
                        if "Whole" in next_state: transition_matrix[i][j] = difficulty_tiers[4] if difficulty_level >= difficulty_divisors[4] else 0
                        elif "Half" in next_state: transition_matrix[i][j] = difficulty_tiers[4] if difficulty_level>=difficulty_divisors[4] else 0
                        elif "Quarter" in next_state: transition_matrix[i][j] = difficulty_tiers[5] if difficulty_level>=difficulty_divisors[5] else 0
                        elif "Eighth" in next_state: transition_matrix[i][j] = difficulty_tiers[9] if difficulty_level>=difficulty_divisors[9] else 0
                        elif "Sixteenth" in next_state: transition_matrix[i][j] = 0 #needs to be a null event because nothing can always fill the remaining beats after a dotted 16th unless subdividing more with 32nds, etc.
                        else: transition_matrix[i][j] = 0

                else:
                        if "Whole" in next_state: transition_matrix[i][j] = difficulty_tiers[1] if difficulty_level>=difficulty_divisors[1] else 0
                        elif "Half" in next_state: transition_matrix[i][j] = difficulty_tiers[1] if difficulty_level>=difficulty_divisors[1] else 0
                        elif "Quarter" in next_state: transition_matrix[i][j] = difficulty_tiers[1] if difficulty_level>=difficulty_divisors[1] else 0
                        elif "Eighth" in next_state: transition_matrix[i][j] = difficulty_tiers[2] if difficulty_level>=difficulty_divisors[2] else 0
                        elif "Sixteenth" in next_state: transition_matrix[i][j] = difficulty_tiers[7] if difficulty_level>=difficulty_divisors[7] else 0
                        else: transition_matrix[i][j] = 0
                
                if "Rest" in next_state: transition_matrix[i][j]/=5 #make rests occur less frequently
            
    #'''
    # Normalize the matrix
    for i in range(num_states):
        row_sum = sum(transition_matrix[i])
        if row_sum > 0:
            transition_matrix[i] = [p / row_sum for p in transition_matrix[i]]
        else:
            # Handle the case where the row sum is 0
            transition_matrix[i] = [0 for _ in transition_matrix[i]]  # Keeping it as all 0s

    print("Transition Matrix:\n", transition_matrix)
    return transition_matrix, states, num_states

def get_time_signature():
    while True:
        time_sig_input = input("Enter the time signature in the format x/y (e.g., 4/4 or 3/4): ")
        try:
            x, y = map(int, time_sig_input.split('/'))
            return [x, y]
        except ValueError:
            print("Invalid format. Please enter the time signature as two integers separated by a slash (e.g., 4/4).")

time_signature = get_time_signature()

def get_difficulty_level():
    while True:
        try:
            difficulty_level = float(input(
                    "Enter the difficulty level (must be a number >= 1, decimals allowed):\n"
                    "1+ : Includes quarter, half, and whole notes.\n"
                    "2+ : Adds eighth notes.\n"
                    "3+ : Adds basic types of triplets.\n"
                    "...\n"
                    "7+ : Adds sixteenth notes.\n"
                    ">7 : More complex rhythms.\n"
                    "For melodic components, in addition to the previous conditions, a higher difficulty will increase the note range and maximum jump.\n"
                    "Enter difficulty level: "))

            if difficulty_level >= 1:
                return difficulty_level
            else:
                print("Please enter a number greater than or equal to 1.")
        except ValueError:
            print("Invalid input. Please enter a numerical value.")

difficulty_level = get_difficulty_level()

transition_matrix, states, num_states = generate_rhythm_matrix(rhythmic_elements, rhythmic_values, difficulty_level, time_signature)

def normalize_beat(beat, time_signature):
    # Normalize the beat to the nearest expected value, such as 1, 2, 3, or 4 in a 4/4 time signature
    normalized_beat = round(beat * 12) / 12  # Assuming the smallest rhythmic element is a twelfth of a beat
    return normalized_beat if normalized_beat <= time_signature[0] else normalized_beat % time_signature[0]

def generate_n_notes(length=200):
    rhythm = []
    current_beat = 1  # Start at Beat 1

    # Filter for states at Beat 1 that are either quarter or eighth notes
    if difficulty_level <= 1:
        possible_start_states = [state for state in states 
                                if round(float(state.split(" Beat ")[1]), 3) == 1.0 and
                                ("Quarter" in state) and
                                "Dotted" not in state
                                and "Triplet" not in state]
    elif difficulty_level <= 5:
        possible_start_states = [state for state in states 
                                if round(float(state.split(" Beat ")[1]), 3) == 1.0 and
                                ("Quarter" in state or "Eighth" in state) and
                                "Triplet" not in state and 
                                "Dotted Eighth" not in state and
                                "Dotted Quarter" not in state]
    else: 
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
        current_beat = normalize_beat(current_beat, time_signature)
        
        # Filter states based on the current beat
        possible_states_indices = [i for i, state in enumerate(states)
                                   if normalize_beat(float(state.split(" Beat ")[1]), time_signature) == current_beat]
        

        if not possible_states_indices:
            print(f"Error/End: No valid states to choose from at beat {current_beat}")
            break

        # Calculate the sum of probabilities for the filtered states
        probabilities = [transition_matrix[current_state_index][i] for i in possible_states_indices]
        probabilities_sum = sum(probabilities)

        if probabilities_sum == 0:
            print(f"Error/End: No valid transition from {states[current_state_index]}")
            break

        # Normalize probabilities for the filtered states
        normalized_probabilities = [p / probabilities_sum for p in probabilities]

        # Choose the next state index from the filtered states based on normalized probabilities
        current_state_index = np.random.choice(possible_states_indices, p=normalized_probabilities)
        current_state = states[current_state_index]
        
        rhythm.append(current_state)

        # Update the current beat based on the duration of the new current state
        current_beat += calculate_duration(current_state)

    return rhythm

# Normalize the transition matrix
for i in range(num_states):
    row_sum = sum(transition_matrix[i])
    if row_sum > 0:
        transition_matrix[i] = [p / row_sum for p in transition_matrix[i]]
    else:
        # Assign equal probabilities if a row sums to 0
        transition_matrix[i] = [1.0 / num_states for _ in transition_matrix[i]]


def get_number_of_notes():
    while True:
        try:
            num_notes = int(input("Enter the number of notes (must be a positive integer no less than 1): "))
            if num_notes >= 1:
                return num_notes
            else:
                print("The number must be no less than 1. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a positive integer.")

num_notes = get_number_of_notes()

# Generate a sample rhythm
sample_rhythm = generate_n_notes(num_notes)
print("Sample Rhythm:", sample_rhythm)


def rhythm_to_lilypond(rhythm):
    lilypond_notes = []
    triplet_open = False
    triplet_count = 0

    # Mapping for standard durations
    duration_mapping = {
        "Whole": "1",
        "Half": "2",
        "Quarter": "4",
        "Eighth": "8",
        "Sixteenth": "16",
        "Dotted Whole": "1.",
        "Dotted Half": "2.",
        "Dotted Quarter": "4.",
        "Dotted Eighth": "8.",
        "Dotted Sixteenth": "16."
    }

    # Mapping to adjust triplet note types
    triplet_adjustment = {
        "Whole Triplet": "Half",
        "Half Triplet": "Quarter",
        "Quarter Triplet": "Eighth",
        "Eighth Triplet": "Sixteenth"
    }

    for r in rhythm:
        components = r.split()
        is_rest = "Rest" in components
        is_triplet = "Triplet" in r

        # Determine note type and handle dotted notes correctly
        if "Dotted" in components:
            note_type = "Dotted " + components[1]
        else:
            note_type = components[0]

        #print(note_type)
        # Adjust the note type for triplets
        if is_triplet:
            for triplet_type, adjusted_type in triplet_adjustment.items():
                if triplet_type in r:
                    note_type = adjusted_type
                    break

        lily_duration = duration_mapping.get(note_type, "4")

        if is_triplet:
            # Extract just the numerical part after "Triplet"
            triplet_num = int(''.join(filter(str.isdigit, components[2])))

            if triplet_num == 1 and not triplet_open:
                lilypond_notes.append("\\tuplet 3/2 { ")
                triplet_open = True
                triplet_count = 0

            note_or_rest_char = 'r' if is_rest else 'c'
            octave = "" if is_rest else "'"
            lilypond_notes.append(f"{note_or_rest_char}{octave}{lily_duration} ")

            triplet_count += 1
            if triplet_count == 3 and triplet_open:
                lilypond_notes.append("} ")
                triplet_open = False
        else:
            note_or_rest_char = 'r' if is_rest else 'c'
            octave = "" if is_rest else "'"
            lilypond_notes.append(f"{note_or_rest_char}{octave}{lily_duration} ")

    # Ensure any open triplets are properly closed
    if triplet_open:
        lilypond_notes.append("} ")

    return " ".join(lilypond_notes)



lilypond_string = rhythm_to_lilypond(sample_rhythm)

# This will produce a string like "c'4 c,8 c'4" that you can then embed into a LilyPond script
print(lilypond_string)

import subprocess
import os
from PIL import Image

def display_music_lilypond(lilypond_string):
    # Create a full LilyPond script with dynamic time signature
    script = f"""
    \\version "2.20.0"
    \\score {{
        \\new RhythmicStaff {{
            \\time {time_signature[0]}/{time_signature[1]}
            {lilypond_string}
        }}
        \\layout {{ }}
        \\midi {{ }}
    }}
    """

    # Write the script to a file named "rhythm.ly"
    with open("rhythm.ly", "w") as file:
        file.write(script)

    # Call LilyPond to compile the file into a PNG image
    subprocess.run(["lilypond", "--png", "-o", "rhythm", "rhythm.ly"])

    # Open and display the generated PNG file
    if os.path.exists("rhythm.png"):
        img = Image.open("rhythm.png")
        img.show()
    else:
        print("Error: PNG file not found. Check LilyPond compilation.")

# Example usage
display_music_lilypond(lilypond_string)

def return_for_pitch_generation():
    return lilypond_string, time_signature, difficulty_level