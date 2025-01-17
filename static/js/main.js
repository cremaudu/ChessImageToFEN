document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadBtn = document.getElementById('upload-btn');
    const preview = document.getElementById('preview');
    const previewImage = document.getElementById('preview-image');
    const analyzeBtn = document.getElementById('analyze-btn');
    const result = document.getElementById('result');
    const fenResult = document.getElementById('fen-result');
    const copyBtn = document.getElementById('copy-btn');

    // Gestion du drag & drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('dragover');
        });
    });

    dropZone.addEventListener('drop', handleDrop);
    uploadBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    analyzeBtn.addEventListener('click', analyzeImage);
    copyBtn.addEventListener('click', copyFEN);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFileSelect(e) {
        const files = e.target.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    previewImage.src = e.target.result;
                    dropZone.hidden = true;
                    preview.hidden = false;
                    result.hidden = true;
                };
                reader.readAsDataURL(file);
            }
        }
    }

    async function analyzeImage() {
        const formData = new FormData();
        const file = fileInput.files[0];
        formData.append('image', file);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (response.ok) {
                fenResult.value = data.fen;
                result.hidden = false;
            } else {
                alert(data.error || 'Une erreur est survenue lors de l\'analyse');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Une erreur est survenue lors de l\'analyse');
        }
    }

    async function copyFEN() {
        try {
            await navigator.clipboard.writeText(fenResult.value);
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'Copié !';
            setTimeout(() => {
                copyBtn.textContent = originalText;
            }, 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
        }
    }

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
        document.getElementById('results').style.display = 'block';
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
        const fen = document.getElementById('fenInput').value;
        if (await copyToClipboard(fen)) {
            alert('FEN copié dans le presse-papiers !');
        }
    }

    // Copie du PGN
    async function copyPgn() {
        const pgn = document.getElementById('pgnText').value;
        if (await copyToClipboard(pgn)) {
            alert('PGN copié dans le presse-papiers !');
        }
    }

    // Téléchargement du PGN
    function downloadPgn() {
        const pgn = document.getElementById('pgnText').value;
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
        const container = document.getElementById('variationsList');
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
    document.getElementById('uploadForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        const fileInput = document.getElementById('imageFile');
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
                document.getElementById('originalImage').src = URL.createObjectURL(fileInput.files[0]);
                
                // Affiche l'échiquier SVG
                document.getElementById('boardSvg').innerHTML = data.board_svg;
                
                // Met à jour le FEN
                document.getElementById('fenInput').value = data.fen;
                
                // Met à jour l'analyse
                document.getElementById('analysisResult').textContent = data.analysis_summary;
                if (data.variations) {
                    displayVariations(data.variations);
                }
                
                // Met à jour le PGN
                document.getElementById('pgnText').value = data.pgn;
                
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
    document.getElementById('imageFile').addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            document.getElementById('originalImage').src = URL.createObjectURL(file);
            showResults();
        }
    });
});
