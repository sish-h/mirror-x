from flask import Flask, render_template_string
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>MIRROR-X - Live</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a1a; color: white; text-align: center; padding: 50px; }
        .container { max-width: 800px; margin: 0 auto; }
        .logo { font-size: 3rem; margin-bottom: 1rem; }
        .status { color: #4a9eff; font-size: 1.5rem; margin: 1rem 0; }
        .features { margin: 2rem 0; }
        .feature { background: #2a2a2a; padding: 1rem; margin: 0.5rem 0; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">MIRROR-X</div>
        <div class="status">LIVE</div>
        <h1>Your Study Accountability System</h1>
        <div class="features">
            <div class="feature">AI Chat System</div>
            <div class="feature">Study Tracking</div>
            <div class="feature">Mirror-X Behavioral Engine</div>
            <div class="feature">Leaderboard</div>
            <div class="feature">Transformation Mode</div>
            <div class="feature">Weekly Reports</div>
        </div>
        <p><strong>Status:</strong> All systems operational</p>
        <p><em>This is a live deployment of MIRROR-X</em></p>
    </div>
</body>
</html>
""")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
