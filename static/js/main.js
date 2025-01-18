document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('imageFile');
    const uploadForm = document.getElementById('uploadForm');
    const results = document.getElementById('results');
    const originalImage = document.getElementById('originalImage');
    const boardSvg = document.getElementById('boardSvg');
    const fenInput = document.getElementById('fenInput');
    const analysisResult = document.getElementById('analysisResult');
    const pgnText = document.getElementById('pgnText');
    const variationsList = document.getElementById('variationsList');

    // Fonctions utilitaires
    function showLoading() {
        document.querySelector('.loading').style.display = 'flex';
        document.querySelector('.loading-backdrop').style.display = 'block';
    }

    function hideLoading() {
        document.querySelector('.loading').style.display = 'none';
        document.querySelector('.loading-backdrop').style.display = 'none';
    }

    function showResults() {
        results.style.display = 'block';
    }

    // Copie dans le presse-papiers
    async function copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            console.error('Erreur lors de la copie :', err);
            return false;
        }
    }

    // Copie du FEN
    async function copyFen() {
        const fen = fenInput.value;
        if (await copyToClipboard(fen)) {
            alert('FEN copié dans le presse-papiers !');
        }
    }

    // Copie du PGN
    async function copyPgn() {
        const pgn = pgnText.value;
        if (await copyToClipboard(pgn)) {
            alert('PGN copié dans le presse-papiers !');
        }
    }

    // Téléchargement du PGN
    function downloadPgn() {
        const pgn = pgnText.value;
        const blob = new Blob([pgn], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        
        // Génère un nom de fichier avec la date
        const date = new Date().toISOString().split('T')[0];
        a.download = `chess_position_${date}.pgn`;
        
        a.href = url;
        a.click();
        window.URL.revokeObjectURL(url);
    }

    // Affichage des variations
    function displayVariations(variations) {
        const container = variationsList;
        container.innerHTML = '';
        
        variations.forEach((variation, index) => {
            const div = document.createElement('div');
            div.className = 'mb-3';
            
            // En-tête de la variation
            const header = document.createElement('h6');
            header.className = 'mb-2';
            header.textContent = `Variante ${index + 1}`;
            
            // Score ou mat
            const score = document.createElement('span');
            score.className = 'badge bg-secondary ms-2';
            if (variation.mate_in !== null) {
                score.textContent = `Mat en ${variation.mate_in}`;
                score.className += ' bg-danger';
            } else {
                score.textContent = `${(variation.score / 100).toFixed(2)}`;
                if (variation.score > 0) score.className += ' bg-success';
            }
            header.appendChild(score);
            
            // Coups de la variante
            const moves = document.createElement('div');
            moves.className = 'small text-muted';
            moves.textContent = variation.pv.join(' ');
            
            div.appendChild(header);
            div.appendChild(moves);
            container.appendChild(div);
        });
    }

    // Gestionnaire de formulaire
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        
        showLoading();
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Affiche l'image originale
                originalImage.src = URL.createObjectURL(fileInput.files[0]);
                
                // Affiche l'échiquier SVG
                boardSvg.innerHTML = data.board_svg;
                
                // Met à jour le FEN
                fenInput.value = data.fen;
                
                // Met à jour l'analyse
                analysisResult.textContent = data.analysis_summary;
                if (data.variations) {
                    displayVariations(data.variations);
                }
                
                // Met à jour le PGN
                pgnText.value = data.pgn;
                
                showResults();
            } else {
                alert('Erreur: ' + data.error);
            }
        } catch (error) {
            console.error('Erreur:', error);
            alert('Erreur lors de l\'analyse: ' + error);
        } finally {
            hideLoading();
        }
    });

    // Prévisualisation de l'image
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            originalImage.src = URL.createObjectURL(file);
            showResults();
        }
    });
});
