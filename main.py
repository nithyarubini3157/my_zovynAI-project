import os
from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CyberZovyn AI Mentor</title>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
    <style>
        body {
            background-color: #0d1117;
            color: #c9d1d9;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .header {
            width: 100%;
            max-width: 800px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #30363d;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .title {
            font-size: 24px;
            font-weight: bold;
            color: #58a6ff;
        }
        .stats {
            display: flex;
            gap: 15px;
        }
        .badge {
            background-color: #238636;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
        }
        .score {
            background-color: #1f6feb;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
        }
        .chat-box {
            width: 100%;
            max-width: 800px;
            height: 450px;
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            overflow-y: auto;
            padding: 15px;
            box-sizing: border-box;
            margin-bottom: 15px;
        }
        .message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 6px;
            line-height: 1.5;
        }
        .user-msg {
            background-color: #21262d;
            border-left: 4px solid #58a6ff;
        }
        .ai-msg {
            background-color: #0d1117;
            border-left: 4px solid #238636;
        }
        .level-up-msg {
            background-color: #1c2128;
            border: 2px solid #f1e05a;
            border-left: 6px solid #e3b341;
            box-shadow: 0 0 10px rgba(241, 224, 90, 0.3);
        }
        .input-container {
            width: 100%;
            max-width: 800px;
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 12px;
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #c9d1d9;
            font-size: 16px;
        }
        button {
            padding: 12px 24px;
            background-color: #238636;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            font-size: 16px;
        }
        button:hover {
            background-color: #2ea043;
        }
    </style>
</head>
<body>

<div class="header">
    <div class="title">CyberZovyn AI Mentor 🤖</div>
    <div class="stats">
        <span id="levelDisplay" class="badge">ROOKIE</span>
        <span id="scoreDisplay" class="score">Score: 0</span>
    </div>
</div>

<div id="chatBox" class="chat-box">
    <div class="message ai-msg">
        <strong>CyberZovyn AI:</strong> Welcome Agent! Ready to hack your way to the top? Type <strong>"start quiz"</strong> to test your cybersecurity skills!
    </div>
</div>

<div class="input-container">
    <input type="text" id="userInput" placeholder="Type your answer (e.g. A, B, C, D) or ask a question..." onkeydown="if(event.key==='Enter') sendMessage()">
    <button onclick="sendMessage()">Send</button>
</div>

<script>
    let userScore = 0;
    let currentLevel = 'ROOKIE';
    let previousLevel = 'ROOKIE';

    function triggerConfetti() {
        confetti({
            particleCount: 150,
            spread: 90,
            origin: { y: 0.6 }
        });
    }

    function updateScoreAndLevel(isCorrect) {
        if(isCorrect) {
            userScore += 2;
        }
        
        document.getElementById('scoreDisplay').innerText = `Score: ${userScore}`;
        const levelBadge = document.getElementById('levelDisplay');

        if(userScore >= 30) currentLevel = 'CYBER ELITE';
        else if(userScore >= 20) currentLevel = 'PRO HACKER';
        else if(userScore >= 10) currentLevel = 'CYBER SCOUT';
        else currentLevel = 'ROOKIE';

        levelBadge.innerText = currentLevel;

        // Catchy Level Up Banner with Level Name
        if(currentLevel !== previousLevel) {
            previousLevel = currentLevel;
            triggerConfetti();

            let catchyBanner = "";
            if(currentLevel === 'CYBER SCOUT') {
                catchyBanner = "⚡ **EXCELLENT PERFORMANCE! LEVEL UP UNLOCKED!** ⚡<br>🎉 **NEW BADGE ACHIEVED: [ CYBER SCOUT ]** 🎉<br>*Unstoppable drive, Agent! You have officially stepped out of the rookie zone!* 🔥";
            } else if(currentLevel === 'PRO HACKER') {
                catchyBanner = "🔥 **OUTSTANDING SKILLS! LEVEL UP UNLOCKED!** 🔥<br>🎉 **NEW BADGE ACHIEVED: [ PRO HACKER ]** 🎉<br>*Brilliant mind at work! You are decoding threats like an absolute pro!* 🎯";
            } else if(currentLevel === 'CYBER ELITE') {
                catchyBanner = "👑 **LEGENDARY STATUS ACHIEVED! LEVEL UP UNLOCKED!** 👑<br>🎉 **NEW BADGE ACHIEVED: [ CYBER ELITE ]** 🎉<br>*Masterclass performance! You have reached the ultimate pinnacle of cyber defense!* 🏆";
            }

            appendCustomMessage(catchyBanner, 'level-up-msg');
        }
    }

    function appendMessage(text, className) {
        const chatBox = document.getElementById('chatBox');
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${className}`;
        msgDiv.innerHTML = text.replace(/\\n/g, '<br>').replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function appendCustomMessage(htmlContent, className) {
        const chatBox = document.getElementById('chatBox');
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${className}`;
        msgDiv.innerHTML = htmlContent;
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function sendMessage() {
        const input = document.getElementById('userInput');
        const message = input.value.trim();
        if(!message) return;

        appendMessage(`<strong>You:</strong> ${message}`, 'user-msg');
        input.value = '';

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message, score: userScore, level: currentLevel })
            });

            const data = await response.json();
            
            if(data.is_correct !== undefined) {
                updateScoreAndLevel(data.is_correct);
            }

            appendMessage(`<strong>CyberZovyn AI:</strong> ${data.reply}`, 'ai-msg');
        } catch(e) {
            appendMessage(`<strong>CyberZovyn AI:</strong> Error connecting to server!`, 'ai-msg');
        }
    }
</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_msg = data.get('message', '').strip()
    score = data.get('score', 0)
    level = data.get('level', 'ROOKIE')

    if not GEMINI_API_KEY:
        return jsonify({'reply': 'GEMINI_API_KEY environment variable is not configured!'})

    model = genai.GenerativeModel('gemini-1.5-flash')

    system_prompt = f"""
    You are CyberZovyn AI Mentor, an interactive cybersecurity quiz tutor.
    User current score: {score}, Level: {level}.

    RULES:
    1. If the user provides a quiz option answer (A, B, C, or D):
       - If Correct: Start response with "CORRECT! 🎉" followed by a short 1-line explanation. Add a catchy compliment like "Sharpshooter moves!", "Bulletproof defense!", or "Flawless execution!".
       - If Incorrect: Start response with "NOT QUITE! 💪" followed by a warm, highly motivating message like "Great attempt, Agent! Every mistake is a system upgrade!", "Don't back down! Learn the fix and hit back stronger!", or "Shake it off, Agent! True hackers learn from errors!". Then explain the correct answer clearly.
       - Then generate 1 new unique multiple-choice question (A, B, C, D) based on cybersecurity concepts appropriate for level {level}.

    2. If user types "start quiz" or asks a question, answer engagingly and present a quiz question.
    """

    try:
        response = model.generate_content(f"{system_prompt}\nUser input: {user_msg}")
        reply_text = response.text

        is_correct = None
        if "CORRECT!" in reply_text:
            is_correct = True
        elif "NOT QUITE!" in reply_text:
            is_correct = False

        return jsonify({'reply': reply_text, 'is_correct': is_correct})
    except Exception as e:
        return jsonify({'reply': f'Error generating response: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)