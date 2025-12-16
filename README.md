# Hybrid Movie Recommendation Engine

A personalized movie recommendation system demonstrating a **Hybrid Approach**: combining **Content-Based Filtering** (TF-IDF on Genres) and **Collaborative Filtering** (User-User similarity). Features an explainable AI dashboard.

## Features

- **Hybrid Recommendation Algorithm**: Weights both content similarity (genres) and collaborative patterns (user behavior) for robust predictions.
- **Explainable AI (XAI)**: The UI decomposes recommendations into "Content Score" vs. "Collaborative Score" to visualize *why* a movie was suggested.
- **Scalable Architecture**: Built with Pandas and Scikit-Learn for efficient matrix computations.
- **Interactive Dashboard**: Modern Flask-based web interface for exploring recommendations.

## Tech Stack

- **Core**: Python 3.12, Pandas, NumPy
- **Machine Learning**: Scikit-Learn (TF-IDF, Cosine Similarity)
- **Web**: Flask (Backend), HTML/CSS/JS (Frontend)
- **Dataset**: MovieLens Small Dataset

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd hybrid-movie-recommender
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Run the Web Interface
Start the dashboard to interactively analyze users and see explainable recommendations.

```bash
python app.py
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

### Run CLI Verification
Run the main script to verify the engine logic in the terminal.

```bash
python main.py
```

## How It Works

1. **Content-Based (The "Genre" Match)**:
   - Uses TF-IDF to vectorize movie genres.
   - Computes Cosine Similarity between a user's liked movies and all other movies.
   - *Result*: Recommendation of movies with similar themes.

2. **Collaborative Filtering (The "People" Match)**:
   - Builds a User-Item rating matrix.
   - Using Cosine Similarity, finds users with similar taste.
   - Predicts ratings based on the weighted average of similar users' ratings.
   - *Result*: Recommendation of movies liked by "people like you".

3. **Hybrid Weighing**:
   - The final score is a weighted sum (default 50/50) of both components, offering a balanced suggestion list.

## License

MIT License. See [LICENSE](LICENSE) for details.
