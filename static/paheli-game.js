// --- CONFIG ---
const TOTAL_LEVELS = 10;
let currentLevel = 1;
let isProcessing = false;

// DOM Elements (Screens)
const levelScreen = document.getElementById('levelScreen');
const gameScreen = document.getElementById('gameScreen');
const levelsGrid = document.getElementById('levelsGrid');

// DOM Elements (Game)
const questionText = document.getElementById('questionText');
const optionsGrid = document.getElementById('optionsGrid');
const currentLevelDisplay = document.getElementById('currentLevelDisplay');

// DOM Elements (Rewards & Popup - ADDED)
const liveBalance = document.getElementById('liveBalance');
const rewardPopup = document.getElementById('rewardPopup');
const wonAmount = document.getElementById('wonAmount');

// Init
document.addEventListener('DOMContentLoaded', () => {
    generateLevels();
    // Agar pehle se balance hai to update UI (Optional)
});

// --- UI FUNCTIONS ---
function showScreen(screen) {
    if(screen === 'gameScreen') {
        if(levelScreen) levelScreen.classList.add('hidden');
        if(gameScreen) gameScreen.classList.remove('hidden');
    } else {
        if(gameScreen) gameScreen.classList.add('hidden');
        if(levelScreen) levelScreen.classList.remove('hidden');
    }
}

function generateLevels() {
    if(!levelsGrid) return; // Safety check
    levelsGrid.innerHTML = '';
    for(let i=1; i<=TOTAL_LEVELS; i++) {
        const btn = document.createElement('div');
        btn.className = 'level-btn';
        btn.innerText = i;
        
        // Level Lock Logic can be added here
        btn.onclick = () => startLevel(i);
        
        levelsGrid.appendChild(btn);
    }
}

// --- GAME LOGIC ---
function startLevel(lvl) {
    currentLevel = lvl;
    if(currentLevelDisplay) currentLevelDisplay.innerText = `LEVEL ${lvl}`;
    showScreen('gameScreen');
    loadRiddle();
}

// Global wrapper to be called by HTML Button in Popup
function nextRiddleFromPopup() {
    loadRiddle();
}

async function loadRiddle() {
    // 1. Reset UI & Popup
    if(rewardPopup) rewardPopup.classList.remove('show'); // Hide Popup
    isProcessing = false;
    
    if(questionText) questionText.innerHTML = '<span class="glow-text" style="color:cyan">🔮 Searching Brain...</span>';
    if(optionsGrid) optionsGrid.innerHTML = '';

    try {
        const res = await fetch('/api/get_riddle', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: USER_ID, // HTML Variable
                level: currentLevel
            })
        });

        const data = await res.json();

        if(data.status === 'completed') {
            questionText.innerHTML = "🎉 Level Complete!<br><button class='opt-btn' onclick='showScreen(\"levelScreen\")'>BACK TO LEVELS</button>";
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
    questionText.innerText = riddle.question;
    
    // Shuffle Options
    let opts = [...riddle.options].sort(() => Math.random() - 0.5);

    opts.forEach(opt => {
        const btn = document.createElement('button');
        btn.className = 'opt-btn'; // Updated class name to match CSS
        btn.innerText = opt;
        
        // Pass ID and Correct Answer for checking
        btn.onclick = () => checkAnswer(btn, opt, riddle.answer, riddle.id);
        
        optionsGrid.appendChild(btn);
    });
}

async function checkAnswer(btn, selected, correct, riddleId) {
    if(isProcessing) return;
    isProcessing = true;

    if(selected === correct) {
        // --- CORRECT ANSWER ---
        btn.classList.add('correct');
        
        // 1. Save Progress & Get Money
        const res = await fetch('/api/submit_answer', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: USER_ID,
                riddle_id: riddleId,
                is_correct: true
            })
        });

        const data = await res.json();

        if(data.status === 'success') {
            // 2. Update Header Balance
            if(liveBalance) liveBalance.innerText = data.new_balance.toLocaleString();

            // 3. Update Reward Popup Text
            const prizeText = data.msg.split('Won ')[1] || "Reward"; 
            if(wonAmount) wonAmount.innerText = "+ " + prizeText;

            // 4. Show Popup (No Auto Load, Wait for User)
            setTimeout(() => {
                if(rewardPopup) rewardPopup.classList.add('show');
            }, 500);
        }

    } else {
        // --- WRONG ANSWER ---
        btn.classList.add('wrong');
        
        // Highlight correct one (Educational)
        Array.from(optionsGrid.children).forEach(b => {
            if(b.innerText === correct) b.classList.add('correct');
        });
        
        // Reset so user can see they were wrong, then maybe retry or load next manually?
        // For now, let's keep them on screen to click 'Back' or Reload manually if stuck,
        // OR auto-reload next riddle after delay (User preference: Hard Mode)
        
        // Agar "Hard Mode" hai to galat hone par bhi next riddle load kar sakte hain
        // lekin abhi hum bas rok dete hain taaki wo padh sakein.
        setTimeout(() => {
             // Optional: loadRiddle(); // Agar auto-next chahiye galat par
             isProcessing = false; // Allow clicking other buttons if needed
        }, 2000); 
    }
}
