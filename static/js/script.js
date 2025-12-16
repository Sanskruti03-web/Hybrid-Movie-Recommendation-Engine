document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const userIdInput = document.getElementById('userIdInput');
    const resultsArea = document.getElementById('resultsArea');
    const historyGrid = document.getElementById('historyGrid');
    const recsGrid = document.getElementById('recsGrid');
    const loader = document.getElementById('loader');
    const errorMsg = document.getElementById('errorMsg');

    analyzeBtn.addEventListener('click', fetchRecommendations);

    async function fetchRecommendations() {
        const userId = userIdInput.value;
        if (!userId) return;

        // UI Reset
        resultsArea.classList.add('hidden');
        errorMsg.classList.add('hidden');
        loader.classList.remove('hidden');

        try {
            const response = await fetch(`/api/recommendations/${userId}`);
            const data = await response.json();

            if (data.error) {
                showError(data.error);
                return;
            }

            renderHistory(data.history);
            renderRecommendations(data.recommendations);

            loader.classList.add('hidden');
            resultsArea.classList.remove('hidden');

        } catch (err) {
            showError("Failed to fetch data. Ensure server is running.");
        }
    }

    function showError(msg) {
        loader.classList.add('hidden');
        errorMsg.textContent = msg;
        errorMsg.classList.remove('hidden');
    }

    function renderHistory(movies) {
        historyGrid.innerHTML = movies.map(movie => `
            <div class="card">
                <h3>${movie.title}</h3>
                <div class="meta">
                    <span>${movie.genres.split('|')[0]}</span>
                    <span>⭐ ${movie.rating}</span>
                </div>
            </div>
        `).join('');
    }

    function renderRecommendations(movies) {
        recsGrid.innerHTML = movies.map(movie => {
            const contentPct = Math.round(movie.content_score * 100);
            const collabPct = Math.round(movie.collab_score * 100);
            const totalScore = (movie.hybrid_score * 100).toFixed(1);

            return `
            <div class="card">
                <div class="total-score">${totalScore}% Match</div>
                <h3>${movie.title}</h3>
                <div class="meta">
                    <span>${movie.genres.split('|').slice(0, 2).join(', ')}</span>
                </div>
                
                <div class="score-breakdown">
                    <div class="label-row">
                        <span>Content (Genre)</span>
                        <span style="color: var(--secondary)">${contentPct}%</span>
                    </div>
                    <div class="bar-container">
                        <div class="bar-bg">
                            <div class="bar-fill fill-content" style="width: ${contentPct}%"></div>
                        </div>
                    </div>
                </div>

                <div class="score-breakdown">
                    <div class="label-row">
                        <span>Collaborative (People)</span>
                        <span style="color: var(--accent)">${collabPct}%</span>
                    </div>
                    <div class="bar-container">
                        <div class="bar-bg">
                            <div class="bar-fill fill-collab" style="width: ${collabPct}%"></div>
                        </div>
                    </div>
                </div>
            </div>
            `;
        }).join('');
    }
});
