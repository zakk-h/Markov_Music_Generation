import pickle
import os

#Goal:Caching 40 different matrices for rhythm and 10 different matrices for pitch.

def generate_matrix(difficulty_level, time_signature):
    #To be done
    matrix = [[difficulty_level, time_signature]]  
    return matrix

def save_cache_to_file(cache, filename):
    with open(filename, "wb") as f:
        pickle.dump(cache, f)

def load_cache_from_file(filename):
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            return pickle.load(f)
    return {}

def get_or_generate_matrix(difficulty_level, time_signature, cache):
    key = (difficulty_level, time_signature)
    if key in cache:
        return cache[key]
    else:
        matrix = generate_matrix(difficulty_level, time_signature)
        cache[key] = matrix
        return matrix

# Main logic
def main():
    cache_file = "matrix_cache.pkl"
    cache = load_cache_from_file(cache_file)

    difficulty_levels = range(1, 11)  # Difficulty levels 1 through 10
    time_signatures = [(5, 4), (4, 4), (3, 4), (2, 4), (7, 4)]  # Time signatures

    # Generate and cache matrices for all combinations
    for difficulty_level in difficulty_levels:
        for time_signature in time_signatures:
            matrix = get_or_generate_matrix(difficulty_level, time_signature, cache)

    # Save the updated cache to a file
    save_cache_to_file(cache, cache_file)

    # Example usage: Retrieve a matrix
    retrieved_matrix = get_or_generate_matrix(7, (4, 4), cache)
    print("Retrieved Matrix:", retrieved_matrix)

if __name__ == "__main__":
    main()
