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
        * { box-sizing: border-box; }
        body {
            background-color: #0b0f19;
            color: #e2e8f0;
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            width: 100%;
            max-width: 900px;
            background: #111827;
            border: 1px solid #1f2937;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #1f2937;
            padding-bottom: 16px;
        }
        .title {
            font-size: 22px;
            font-weight: 700;
            color: #38bdf8;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .stats {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .badge {
            background-color: #ef4444;
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 13px;
            text-transform: uppercase;
        }
        .score {
            background-color: #0284c7;
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 13px;
        }
        .start-btn {
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: white;
            border: none;
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: 600;
            cursor: pointer;
            font-size: 13px;
        }
        .chat-box {
            height: 420px;
            background-color: #0b0f19;
            border: 1px solid #1f2937;
            border-radius: 8px;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .message {
            padding: 12px 16px;
            border-radius: 8px;
            line-height: 1.5;
            max-width: 85%;
            font-size: 15px;
        }
        .user-msg {
            background-color: #1d4ed8;
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 2px;
        }
        .ai-msg {
            background-color: #1f2937;
            color: #e2e8f0;
            align-self: flex-start;
            border-bottom-left-radius: 2px;
            border-left: 4px solid #38bdf8;
        }
        .level-banner {
            background: linear-gradient(135deg, #1e1b4b, #311b92);
            border: 2px solid #a855f7;
            color: #f3e8ff;
            align-self: center;
            width: 100%;
            text-align: center;
            padding: 14px;
            border-radius: 8px;
            box-shadow: 0 0 15px rgba(168, 85, 247, 0.4);
        }
        .tools-container {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .tool-btn {
            background-color: #1f2937;
            border: 1px solid #374151;
            color: #38bdf8;
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 13px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
        }
        .tool-btn:hover {
            background-color: #374151;
            border-color: #38bdf8;
        }
        .input-container {
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 12px 16px;
            background-color: #0b0f19;
            border: 1px solid #374151;
            border-radius: 8px;
            color: #e2e8f0;
            font-size: 15px;
            outline: none;
        }
        input[type="text"]:focus {
            border-color: #38bdf8;
        }
        .send-btn {
            padding: 12px 24px;
            background-color: #38bdf8;
            color: #0f172a;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 700;
            font-size: 15px;
        }
        .send-btn:hover {
            background-color: #0284c7;
            color: white;
        }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <div class="title">CyberZovyn AI Mentor 🤖</div>
        <div class="stats">
            <span id="levelDisplay" class="badge">ROOKIE</span>
            <span id="scoreDisplay" class="score">Score: 0</span>
            <button class="start-btn" onclick="startQuiz()">🎯 Start Quiz</button>
        </div>
    </div>

    <div id="chatBox" class="chat-box">
        <div class="message ai-msg">
            Welcome Agent! I am <strong>CyberZovyn AI</strong>. Knowledge Base Loaded! Select a tool below or ask any concept! ⚡
        </div>
    </div>

    <div class="tools-container">
        <button class="tool-btn" onclick="sendToolPrompt('Phishing Analyzer')">🔍 Phishing Analyzer</button>
        <button class="tool-btn" onclick="sendToolPrompt('Log Analyzer')">📊 Log Analyzer</button>
        <button class="tool-btn" onclick="sendToolPrompt('Vuln Explainer')">🛡️ Vuln Explainer</button>
    </div>

    <div class="input-container">
        <input type="text" id="userInput" placeholder="Ask a question or paste text to analyze..." onkeydown="if(event.key==='Enter') sendMessage()">
        <button class="send-btn" onclick="sendMessage()">Send</button>
    </div>
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

        if(currentLevel !== previousLevel) {
            previousLevel = currentLevel;
            triggerConfetti();

            let catchyBanner = "";
            if(currentLevel === 'CYBER SCOUT') {
                catchyBanner = "⚡ <strong>EXCELLENT PERFORMANCE! LEVEL UP UNLOCKED!</strong> ⚡<br>🎉 <strong>NEW BADGE ACHIEVED: [ CYBER SCOUT ]</strong> 🎉<br><em>Unstoppable drive, Agent! You have officially stepped out of the rookie zone!</em> 🔥";
            } else if(currentLevel === 'PRO HACKER') {
                catchyBanner = "🔥 <strong>OUTSTANDING SKILLS! LEVEL UP UNLOCKED!</strong> 🔥<br>🎉 <strong>NEW BADGE ACHIEVED: [ PRO HACKER ]</strong> 🎉<br><em>Brilliant mind at work! You are decoding threats like an absolute pro!</em> 🎯";
            } else if(currentLevel === 'CYBER ELITE') {
                catchyBanner = "👑 <strong>LEGENDARY STATUS ACHIEVED! LEVEL UP UNLOCKED!</strong> 👑<br>🎉 <strong>NEW BADGE ACHIEVED: [ CYBER ELITE ]</strong> 🎉<br><em>Masterclass performance! You have reached the ultimate pinnacle of cyber defense!</em> 🏆";
            }

            appendCustomMessage(catchyBanner, 'level-banner');
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

    function startQuiz() {
        document.getElementById('userInput').value = "start quiz";
        sendMessage();
    }

    function sendToolPrompt(toolName) {
        document.getElementById('userInput').value = `Explain ${toolName} and give me a question on it`;
        sendMessage();
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
            appendMessage(`Unable to fetch response.`, 'ai-msg');
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

    # Exact Gemini Model Requested
    model = genai.GenerativeModel('gemini-3.5-flash-lite')

    system_prompt = f"""
    You are CyberZovyn AI Mentor, an interactive cybersecurity quiz tutor.
    User current score: {score}, Level: {level}.

    RULES:
    1. If the user provides a quiz option answer (A, B, C, or D):
       - If Correct: Start response strictly with "CORRECT! 🎉" followed by a short explanation. Add a catchy praise like "Sharpshooter moves!", "Bulletproof defense!", or "Flawless execution!".
       - If Incorrect: Start response strictly with "NOT QUITE! 💪" followed by a warm motivational phrase like "Great attempt, Agent! Every mistake is a system upgrade!", "Don't back down! Learn the fix and hit back stronger!", or "Shake it off! True hackers learn from errors!". Then explain the correct answer clearly.
       - Then generate 1 new unique multiple-choice question (A, B, C, D) based on cybersecurity concepts for level {level}.

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