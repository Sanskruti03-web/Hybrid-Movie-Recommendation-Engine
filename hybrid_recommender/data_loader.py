import os
import zipfile
import requests
import pandas as pd
import io

DATA_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
DATA_DIR = "data"
MOVIES_FILE = os.path.join(DATA_DIR, "ml-latest-small", "movies.csv")
RATINGS_FILE = os.path.join(DATA_DIR, "ml-latest-small", "ratings.csv")

def download_movielens():
    """Downloads and extracts the MovieLens dataset if not already present."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    if os.path.exists(MOVIES_FILE) and os.path.exists(RATINGS_FILE):
        print("Dataset already exists.")
        return

    print("Downloading dataset...")
    response = requests.get(DATA_URL)
    response.raise_for_status()
    
    print("Extracting dataset...")
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall(DATA_DIR)
    print("Download and extraction complete.")

def load_data():
    """Loads movies and ratings data into pandas DataFrames."""
    download_movielens()
    
    print("Loading data...")
    movies = pd.read_csv(MOVIES_FILE)
    ratings = pd.read_csv(RATINGS_FILE)
    
    print(f"Loaded {len(movies)} movies and {len(ratings)} ratings.")
    return movies, ratings

if __name__ == "__main__":
    load_data()
