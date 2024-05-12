import pickle
import gzip
import os

#Save the cache to a file with gzip compression
def save_cache_with_compression(cache, filename):
    with gzip.open(filename, 'wb') as f:
        pickle.dump(cache, f)

#Load the cache from a file with gzip decompression
def load_cache_with_decompression(filename):
    if os.path.exists(filename):
        with gzip.open(filename, 'rb') as f:
            return pickle.load(f)
    return None
