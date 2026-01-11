// --- CONFIG ---
const TOTAL_LEVELS = 10;
let currentLevel = 1;
let isProcessing = false;
let currentRiddle = null;

// DOM Elements
const levelScreen = document.getElementById('levelScreen');
const gameScreen = document.getElementById('gameScreen');
const levelsGrid = document.getElementById('levelsGrid');
const questionText = document.getElementById('questionText');
const optionsGrid = document.getElementById('optionsGrid');
const currentLevelDisplay = document.getElementById('currentLevelDisplay');
const rewardPopup = document.getElementById('rewardPopup');
const wonAmount = document.getElementById('wonAmount');
const liveBalance = document.getElementById('liveBalance');

// Init: Page Load hone par Level Grid banao
document.addEventListener('DOMContentLoaded', () => {
    generateLevels();
    showScreen('levelScreen'); // Pehle Level List dikhao
});

// --- UI FUNCTIONS ---
function showScreen(screenName) {
    if(screenName === 'gameScreen') {
        levelScreen.classList.add('hidden');
        gameScreen.classList.remove('hidden');
    } else {
        gameScreen.classList.add('hidden');
        levelScreen.classList.remove('hidden');
        // Reset game UI
        if(rewardPopup) rewardPopup.classList.remove('show');
    }
}

function generateLevels() {
    levelsGrid.innerHTML = '';
    for(let i=1; i<=TOTAL_LEVELS; i++) {
        const btn = document.createElement('div');
        btn.className = 'level-btn';
        btn.innerText = i;
        btn.onclick = () => startLevel(i); // Click karne par game start
        levelsGrid.appendChild(btn);
    }
}

// --- GAME LOGIC ---
function startLevel(lvl) {
    currentLevel = lvl;
    currentLevelDisplay.innerText = lvl;
    showScreen('gameScreen'); // Game dikhao
    loadRiddle(); // API call karo
}

function nextRiddleFromPopup() {
    loadRiddle();
}

async function loadRiddle() {
    // UI Reset
    rewardPopup.classList.remove('show');
    optionsGrid.innerHTML = '';
    questionText.innerHTML = '<span style="color:cyan">Searching Mystery...</span>';
    isProcessing = false;

    try {
        const res = await fetch('/api/get_riddle', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: USER_ID,
                level: currentLevel  // Ab ye sahi level bhejega
            })
        });

        const data = await res.json();

        if(data.status === 'completed') {
            questionText.innerHTML = "🎉 Level Complete!<br>Go Back to Select Next Level.";
            return;
        }

        if(data.status === 'error') {
            questionText.innerText = "Error: " + data.msg;
            return;
        }

        displayRiddle(data.riddle);

    } catch (e) {
        console.error(e);
        questionText.innerText = "Server Error! Check Console.";
    }
}

function displayRiddle(riddle) {
    currentRiddle = riddle;
    questionText.innerText = riddle.question;
    
    // Shuffle Options
    let opts = [...riddle.options].sort(() => Math.random() - 0.5);

    opts.forEach(opt => {
        const btn = document.createElement('button');
        btn.className = 'opt-btn';
        btn.innerText = opt;
        btn.onclick = () => checkAnswer(btn, opt);
        optionsGrid.appendChild(btn);
    });
}

async function checkAnswer(btn, selected) {
    if(isProcessing) return;
    isProcessing = true;

    if(selected === currentRiddle.answer) {
        btn.classList.add('correct');
        
        // Backend Call
        const res = await fetch('/api/submit_answer', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: USER_ID,
                riddle_id: currentRiddle.id,
                is_correct: true
            })
        });

        const data = await res.json();

        if(data.status === 'success') {
            liveBalance.innerText = data.new_balance.toLocaleString();
            const prizeText = data.msg.split('Won ')[1] || "Reward"; 
            wonAmount.innerText = "+ " + prizeText;

            setTimeout(() => {
                rewardPopup.classList.add('show');
            }, 500);
        } else {
            // Already solved case handling (optional)
            wonAmount.innerText = "+ ₹0 (Replay)";
            setTimeout(() => { rewardPopup.classList.add('show'); }, 500);
        }

    } else {
        btn.classList.add('wrong');
        // Auto Reset Wrong Button
        setTimeout(() => {
            btn.classList.remove('wrong');
            isProcessing = false;
        }, 1000);
    }
}
