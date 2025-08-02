from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>BD Train Tracker</title>
    <style>
        body {
            font-family: sans-serif;
            background: #f0f2f5;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }
        .card {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 400px;
            width: 90%;
        }
        input, button {
            padding: 10px;
            margin: 10px;
            width: 80%;
            font-size: 1rem;
        }
    </style>
</head>
<body>
    <div class="card">
        <h2>🚆 Bangladesh Train Tracker</h2>
        <form method="POST">
            <input type="text" name="train_number" placeholder="Enter Train Number" required>
            <br>
            <button type="submit">Track Train</button>
        </form>

        {% if result %}
            {% if result.error %}
                <p style="color:red;">{{ result.error }}</p>
            {% else %}
                <h3>Train Number: {{ result.train_number }}</h3>
                <p>📍 Current Location: {{ result.current_location }}</p>
                {% if result.delay %}
                    <p>⏳ Delay: {{ result.delay }}</p>
                {% endif %}
            {% endif %}
        {% endif %}
    </div>
</body>
</html>
"""

def get_train_location(train_number):
    try:
        url = f"https://trainseat.onrender.com/live/train/{train_number}"
        res = requests.get(url, timeout=7)
        if res.status_code != 200:
            return {"error": "Train data not found or site unavailable."}

        soup = BeautifulSoup(res.text, 'html.parser')

        # সাধারণত ওয়েবসাইটে লোকেশন বা স্ট্যাটাস div/span এর মধ্যে থাকে, আমরা চেষ্টা করব কিছু সম্ভাব্য ট্যাগ থেকে নিতে
        # আগে ছিল h4, এখন চেষ্টা করব আরো কিছু
        location = None
        delay = None

        # Try finding location inside h4 tag
        h4_tag = soup.find('h4')
        if h4_tag and h4_tag.text.strip():
            location = h4_tag.text.strip()
        
        # কিছু সাইটে delay info span বা p ট্যাগে থাকতে পারে
        delay_tag = soup.find('span', class_='delay') or soup.find('p', class_='delay')

        if delay_tag:
            delay = delay_tag.text.strip()

        if not location:
            return {"error": "Could not find location info."}

        return {
            "train_number": train_number,
            "current_location": location,
            "delay": delay
        }

    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        train_number = request.form.get('train_number').strip()
        if not train_number.isdigit():
            result = {"error": "Train number should be numeric."}
        else:
            result = get_train_location(train_number)
    return render_template_string(TEMPLATE, result=result)

if __name__ == '__main__':
    app.run(debug=True)
