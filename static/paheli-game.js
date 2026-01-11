// --- CONFIG ---
const TOTAL_LEVELS = 10;
let currentLevel = 1;
let isProcessing = false;

// DOM Elements
const levelScreen = document.getElementById('levelScreen');
const gameScreen = document.getElementById('gameScreen');
const levelsGrid = document.getElementById('levelsGrid');
const questionText = document.getElementById('questionText');
const optionsGrid = document.getElementById('optionsGrid');
const currentLevelDisplay = document.getElementById('currentLevelDisplay');

// Init
document.addEventListener('DOMContentLoaded', () => {
    generateLevels();
});

// --- UI FUNCTIONS ---
function showScreen(screen) {
    if(screen === 'gameScreen') {
        levelScreen.classList.add('hidden');
        gameScreen.classList.remove('hidden');
    } else {
        gameScreen.classList.add('hidden');
        levelScreen.classList.remove('hidden');
    }
}

function generateLevels() {
    levelsGrid.innerHTML = '';
    for(let i=1; i<=TOTAL_LEVELS; i++) {
        const btn = document.createElement('div');
        btn.className = 'level-btn';
        btn.innerText = i;
        
        // Level Lock Logic (Optional: Level 1 hamesha unlock)
        // Yahan aap premium logic laga sakte ho
        btn.onclick = () => startLevel(i);
        
        levelsGrid.appendChild(btn);
    }
}

// --- GAME LOGIC ---
function startLevel(lvl) {
    currentLevel = lvl;
    currentLevelDisplay.innerText = `LEVEL ${lvl}`;
    showScreen('gameScreen');
    loadRiddle();
}

async function loadRiddle() {
    isProcessing = false;
    questionText.innerHTML = '<span class="glow-text">🔮 पहेली आ रही है...</span>';
    optionsGrid.innerHTML = '';

    try {
        const res = await fetch('/api/get_riddle', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: USER_ID, // HTML se aa raha hai
                level: currentLevel
            })
        });

        const data = await res.json();

        if(data.status === 'completed') {
            questionText.innerHTML = "🎉 Level Complete! <br> सारी पहेलियां हल हो गईं।";
            return;
        }

        if(data.status === 'error') {
            questionText.innerText = "Error: " + data.msg;
            return;
        }

        displayRiddle(data.riddle);

    } catch (e) {
        console.error(e);
        questionText.innerText = "Server Connection Failed!";
    }
}

function displayRiddle(riddle) {
    // Current riddle data store karein answer check ke liye
    // Note: Security ke liye answer backend pe check hona chahiye, 
    // par UI speed ke liye hum yahan store kar rahe hain (temporary).
    // Backend API should ideally NOT send 'answer' field if strict anti-cheat needed.
    // Assuming backend sends {id, question, options, answer} for simplicity based on prompt.
    
    questionText.innerText = riddle.question;
    
    // Shuffle Options
    let opts = [...riddle.options].sort(() => Math.random() - 0.5);

    opts.forEach(opt => {
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        btn.innerText = opt;
        btn.onclick = () => checkAnswer(btn, opt, riddle.answer, riddle.id);
        optionsGrid.appendChild(btn);
    });
}

async function checkAnswer(btn, selected, correct, riddleId) {
    if(isProcessing) return;
    isProcessing = true;

    if(selected === correct) {
        btn.classList.add('correct');
        // Save Progress
        await fetch('/api/submit_answer', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: USER_ID,
                riddle_id: riddleId,
                is_correct: true
            })
        });
        
        setTimeout(loadRiddle, 1500); // 1.5 sec delay
    } else {
        btn.classList.add('wrong');
        // Highlight correct one
        Array.from(optionsGrid.children).forEach(b => {
            if(b.innerText === correct) b.classList.add('correct');
        });
        
        setTimeout(loadRiddle, 2500); // Thoda zyada time galat jawab dekhne ke liye
    }
}
