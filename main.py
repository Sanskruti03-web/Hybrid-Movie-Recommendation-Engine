from hybrid_recommender.data_loader import load_data
from hybrid_recommender.engine import HybridRecommender
import pandas as pd

def main():
    movies, ratings = load_data()
    
    
    # Initialize Recommender
    # 50% Content (Genre) + 50% Collaborative (User-User)
    recommender = HybridRecommender(content_weight=0.5, collaborative_weight=0.5)
    
    print("Fitting the model... This might take a moment.")
    recommender.fit(movies, ratings)
    
    # Test User
    test_user_id = 1
    
    print(f"\n--- Recommendations for User {test_user_id} ---")
    
    # Show user's history
    user_history = ratings[ratings['userId'] == test_user_id].merge(movies, on='movieId')
    print("\nUser's Top 5 Highest Rated Movies:")
    print(user_history.sort_values(by='rating', ascending=False).head(5)[['title', 'genres', 'rating']])
    
    # Get recommendations
    recommendations = recommender.recommend(test_user_id, top_n=10)
    
    print("\nTop 10 Hybrid Recommendations:")
    print(recommendations)

if __name__ == "__main__":
    main()
