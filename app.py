from flask import Flask, render_template, jsonify, request
from hybrid_recommender.data_loader import load_data
from hybrid_recommender.engine import HybridRecommender
import pandas as pd

app = Flask(__name__)

# Load data and train model once on startup
print("Initializing Recommender System...")
movies, ratings = load_data()
recommender = HybridRecommender(content_weight=0.5, collaborative_weight=0.5)
recommender.fit(movies, ratings)
print("Recommender initialized.")

@app.route('/')
def index():
    return render_template('index.html')
    

@app.route('/api/recommendations/<int:user_id>')
def get_recommendations(user_id):
    try:
        # Get user history context
        user_ratings = ratings[ratings['userId'] == user_id]
        if user_ratings.empty:
            return jsonify({'error': 'User not found or no ratings'}), 404
        
        user_history = user_ratings.merge(movies, on='movieId')
        top_history = user_history.sort_values(by='rating', ascending=False).head(5)
        
        history_data = top_history[['title', 'genres', 'rating']].to_dict(orient='records')
        
        # Get recommendations
        # Let's explain: 
        # Content score comes from similarity to your top movies.
        # Collaborative score comes from what similar users liked.
        recs = recommender.recommend(user_id, top_n=12)
        
        recs_data = recs.to_dict(orient='records')
        
        return jsonify({
            'user_id': user_id,
            'history': history_data,
            'recommendations': recs_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)
