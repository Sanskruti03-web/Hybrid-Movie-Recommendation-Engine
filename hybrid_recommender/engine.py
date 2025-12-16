import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class HybridRecommender:
    def __init__(self, content_weight=0.5, collaborative_weight=0.5):
        self.content_weight = content_weight
        self.collaborative_weight = collaborative_weight
        self.movies = None
        self.ratings = None
        self.tfidf_matrix = None
        self.user_item_matrix = None
        self.user_similarity = None
        self.movie_indices = None
        
    def fit(self, movies, ratings):
        """
        Fits the hybrid recommender models.
        """
        self.movies = movies
        self.ratings = ratings
        
        # --- Content-Based Filtering (TF-IDF on Genres) ---
        print("Training Content-Based Model...")
        # Fill NaN genres with empty string
        self.movies['genres'] = self.movies['genres'].fillna('')
        # Replace separator if needed (MovieLens uses '|')
        self.movies['genres_str'] = self.movies['genres'].str.replace('|', ' ')
        
        tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = tfidf.fit_transform(self.movies['genres_str'])
        
        # Create a mapping from movie_id to index and vice versa
        self.movie_indices = pd.Series(self.movies.index, index=self.movies['movieId']).drop_duplicates()
        
        # --- Collaborative Filtering (User-User) ---
        print("Training Collaborative Model...")
        # Create User-Item Matrix
        self.user_item_matrix = self.ratings.pivot(index='userId', columns='movieId', values='rating').fillna(0)
        
        # Compute User Similarity
        self.user_similarity = cosine_similarity(self.user_item_matrix)
        self.user_similarity_df = pd.DataFrame(self.user_similarity, index=self.user_item_matrix.index, columns=self.user_item_matrix.index)
        
        print("Training Complete.")

    def get_content_recommendations(self, user_id, top_n=50):
        """
        Generates content-based recommendations based on user's highly rated movies.
        """
        # Get user's ratings
        user_ratings = self.ratings[self.ratings['userId'] == user_id]
        if user_ratings.empty:
            return pd.Series()
            
        # Filter for movies the user liked (e.g., rating >= 3.5)
        liked_movies = user_ratings[user_ratings['rating'] >= 3.5]
        if liked_movies.empty:
             # Fallback to all rated movies if no high ratings
            liked_movies = user_ratings
            
        # Get indices of liked movies
        liked_movie_indices = [self.movie_indices[mid] for mid in liked_movies['movieId'] if mid in self.movie_indices]
        
        if not liked_movie_indices:
            return pd.Series()

        # Compute average cosine similarity against all other movies
        # We compute similarity of all movies vs liked movies
        # Shape: (n_movies, n_liked)
        cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix[liked_movie_indices])
        
        # Average similarity scores for each movie
        sim_scores = cosine_sim.mean(axis=1)
        sim_scores_series = pd.Series(sim_scores, index=self.movies['movieId'])
        
        return sim_scores_series

    def get_collaborative_recommendations(self, user_id, top_n=50):
        """
        Generates user-user collaborative filtering recommendations.
        """
        if user_id not in self.user_item_matrix.index:
            return pd.Series()
            
        # Get similar users
        # Sort by similarity, exclude self
        similar_users = self.user_similarity_df[user_id].sort_values(ascending=False).drop(user_id)
        
        # Take top K similar users (e.g., 50) to speed up and reduce noise
        top_similar_users = similar_users.head(50)
        
        # Weighted sum of ratings from similar users
        # (similarities * ratings) / sum(similarities)
        
        # Get ratings of similar users
        similar_users_ratings = self.user_item_matrix.loc[top_similar_users.index]
        
        # Calculate weighted ratings
        weighted_ratings = similar_users_ratings.T.dot(top_similar_users)
        sum_of_weights = top_similar_users.sum()
        
        # Avoid division by zero
        if sum_of_weights == 0:
            return pd.Series()
            
        pred_ratings = weighted_ratings / sum_of_weights
        
        return pred_ratings

    def recommend(self, user_id, top_n=10):
        """
        Generates top-N hybrid recommendations with score breakdown.
        """
        # 1. Get Content-Based Scores
        content_scores = self.get_content_recommendations(user_id, top_n * 2)
        
        # 2. Get Collaborative Scores
        collab_scores = self.get_collaborative_recommendations(user_id, top_n * 2)
        # Normalize collab scores usually 0-5, let's map to 0-1
        if not collab_scores.empty:
            collab_scores = collab_scores / 5.0
        
        # 3. Combine Scores
        all_movies = self.movies['movieId'].unique()
        final_scores = pd.DataFrame(index=all_movies)
        final_scores['content_score'] = content_scores
        final_scores['collab_score'] = collab_scores
        
        # Fill missing with 0
        final_scores.fillna(0, inplace=True)
        
        # Compute Weighted Score
        final_scores['hybrid_score'] = (
            self.content_weight * final_scores['content_score'] + 
            self.collaborative_weight * final_scores['collab_score']
        )
        
        # 4. Filter already watched movies
        watched_movies = self.ratings[self.ratings['userId'] == user_id]['movieId'].tolist()
        final_scores = final_scores.drop(watched_movies, errors='ignore')
        
        # 5. Get Top N
        top_recommendations = final_scores.sort_values(by='hybrid_score', ascending=False).head(top_n)
        
        # Join with movie metadata
        # We merge with index (movieId)
        result = self.movies[self.movies['movieId'].isin(top_recommendations.index)].copy()
        
        # Set index to movieId to match top_recommendations
        result.set_index('movieId', inplace=True)
        
        # Join scores
        result = result.join(top_recommendations[['hybrid_score', 'content_score', 'collab_score']])
        
        result = result.sort_values(by='hybrid_score', ascending=False)
        result.reset_index(inplace=True)
        
        return result[['movieId', 'title', 'genres', 'hybrid_score', 'content_score', 'collab_score']]
