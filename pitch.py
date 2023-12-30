from rhythm import return_for_pitch_generation
import numpy as np
import random

# Fetch rhythm work
lilypond_rhythm_string, time_signature, difficulty_level = return_for_pitch_generation()

# Now you can use the lilypond_rhythm_string and time_signature
print(lilypond_rhythm_string)
print(time_signature)

notes = [1, 1.5, 2, 2.5, 3, 4, 4.5, 5, 5.5, 6, 6.5, 7] #notes in the scale are integers, accidentals are x.5
notes_per_octave = len(notes)
lower_note_bound = 1 #lower bound of range

if round(difficulty_level*2.6,1) > 2.1*notes_per_octave: num_notes = 2.1*notes_per_octave
else: num_notes = round(difficulty_level*2.6,1) # or a user controlled value. a consequence of this value is the upper bound for the range

if difficulty_level*2 > notes[-1]-notes[0]: max_jump = notes[-1]-notes[0]
else: max_jump = difficulty_level*2

def generate_possible_notes_in_range(notes, lower_note_bound, num_notes):
    generated_notes = []
    start_index = notes.index(lower_note_bound)

    octave = 0

    while num_notes > 0:
        for i in range(start_index, len(notes)):
            generated_notes.append(notes[i]+octave)
            num_notes -= 1
            if num_notes == 0:
                break
        start_index = 0  # Reset to start of the notes array for the next cycle
        octave+=7

    return generated_notes

notes_in_range = generate_possible_notes_in_range(notes, lower_note_bound, num_notes)

# Initialize the transition matrix
num_states = len(notes_in_range)
transition_matrix = np.zeros((num_states, num_states))

# Assign probabilities
for i in range(num_states):
    for j in range(num_states):
        note_diff = abs(notes_in_range[j] - notes_in_range[i])
        if note_diff <= max_jump:
            if note_diff == 0:
                transition_matrix[i][j] = 1 / difficulty_level
            else:
                transition_matrix[i][j] = 1 / (note_diff**1.2) #encouraging notes to be in close proximity to each other
                if not notes_in_range[j].is_integer():
                    transition_matrix[i][j] /= 5 #reducing frequency of accidentals

# Normalize the rows of the matrix
for i in range(num_states):
    row_sum = np.sum(transition_matrix[i])
    if row_sum > 0:
        transition_matrix[i] = transition_matrix[i] / row_sum
    else:
        # If a row sums to 0, assign equal probabilities to all transitions
        transition_matrix[i] = np.ones(num_states) / num_states

print(transition_matrix)

# Function to count non-rest notes in the LilyPond rhythm string
def count_non_rest_notes(lilypond_string):
    # Split the string into elements (notes and rests)
    elements = lilypond_string.split()

    # Count elements that are notes and not rests
    non_rest_count = sum(1 for element in elements if not element.startswith('r'))

    return non_rest_count

# Function to generate a sequence of notes using the transition matrix
def generate_note_sequence(transition_matrix, notes_in_range, num_notes):
    note_sequence = []
    current_note_index = random.choice(range(len(notes_in_range)))  # Start from a random note
    note_sequence.append(notes_in_range[current_note_index])

    for _ in range(num_notes - 1):
        probabilities = transition_matrix[current_note_index]
        current_note_index = np.random.choice(len(notes_in_range), p=probabilities)
        note_sequence.append(notes_in_range[current_note_index])

    return note_sequence

# Count the number of non-rest notes in the LilyPond string
num_non_rest_notes = count_non_rest_notes(lilypond_rhythm_string)

# Generate the note sequence
generated_note_sequence = generate_note_sequence(transition_matrix, notes_in_range, num_non_rest_notes)
print(generated_note_sequence)

note_names = ["c", "d", "e", "f", "g", "a", "b"]

def note_to_lilypond(note_value, prev_note_value):
    note_name_index = int(note_value % 7) - 1
    note_name = note_names[note_name_index]
    octave = int((note_value - 1) // 7)  # Ensure octave is an integer
    accidental = ""

    # Determine if it's a sharp or flat based on the previous note
    if note_value % 1 != 0:
        if note_value > prev_note_value:
            accidental = "es"  # Flat
        else:
            accidental = "is"  # Sharp

    # Construct the LilyPond note
    lilypond_note = f"{note_name}{accidental}"
    if octave > 0:
        lilypond_note += "'" * octave  # Add octave marker

    return lilypond_note

# Generate the sequence of LilyPond notes
lilypond_notes = [note_to_lilypond(note, generated_note_sequence[i - 1] if i > 0 else note) 
                  for i, note in enumerate(generated_note_sequence)]

print("lilypond notes")
print(lilypond_notes)
# Split the rhythm string into individual elements
elements = lilypond_rhythm_string.split()

# Replace pitches in the rhythm string with corresponding pitches from lilypond_notes
modified_elements = []
note_index = 0
for element in elements:
    if element.startswith('c'):  # Assuming 'c' is the constant pitch in the rhythm string
        if note_index < len(lilypond_notes):
            # Replace 'c' with the corresponding note from lilypond_notes
            modified_element = lilypond_notes[note_index] + element[1:]
            note_index += 1
        else:
            modified_element = element  # Fallback, in case of mismatch in note counts
    else:
        # Keep rests and other elements unchanged
        modified_element = element
    modified_elements.append(modified_element)

# Recombine into a single LilyPond string
modified_lilypond_music = " ".join(modified_elements)

# Create LilyPond file content
lilypond_content = f"""
\\version "2.20.0"
\\score {{
    \\new Staff {{
        \\time {time_signature[0]}/{time_signature[1]}
        {modified_lilypond_music}
    }}
    \\layout {{ }}
    \\midi {{ }}
}}
"""

print(lilypond_content)

import subprocess
import os
from PIL import Image

# Save to a LilyPond (.ly) file
ly_file = "pitch.ly"
png_file = "pitch.png"  # Name of the output PNG file

with open(ly_file, "w") as file:
    file.write(lilypond_content)

# Call LilyPond to compile the file into a PNG image
subprocess.run(["lilypond", "--png", "-o", "pitch", ly_file])

# Check if the PNG file was created
if os.path.exists(png_file):
    # Open and display the PNG file
    img = Image.open(png_file)
    img.show()
else:
    print("Error: PNG file not found. Check LilyPond compilation.")