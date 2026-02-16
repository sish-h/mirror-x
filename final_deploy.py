import os
import subprocess
import sys
import zipfile

def create_deploy_zip():
    """Create deployment zip file"""
    zip_filename = 'mirror-x-deploy.zip'
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if not file.startswith('.') and not file.endswith('.pyc') and not file.endswith('.zip'):
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, '.'))
    
    print(f"Created {zip_filename}")
    return zip_filename

def deploy_instructions():
    """Print deployment instructions"""
    print("MIRROR-X DEPLOYMENT INSTRUCTIONS")
    print("=" * 50)
    
    print("\n1. RENDER (Recommended):")
    print("   - Go to https://render.com")
    print("   - Sign up and click 'New +' -> 'Web Service'")
    print("   - Connect GitHub repo with your files")
    print("   - Build: pip install -r requirements.txt")
    print("   - Start: gunicorn app:app --bind 0.0.0.0:$PORT")
    print("   - URL: https://your-app.onrender.com")
    
    print("\n2. RAILWAY:")
    print("   - Go to https://railway.app")
    print("   - New Project -> Deploy from GitHub")
    print("   - URL: https://your-app.up.railway.app")
    
    print("\n3. PYTHONANYWHERE:")
    print("   - Go to https://www.pythonanywhere.com")
    print("   - New Web App -> Flask -> Python 3.10")
    print("   - Upload files and configure WSGI")
    print("   - URL: https://yourusername.pythonanywhere.com")
    
    print("\n4. REPLIT:")
    print("   - Go to https://replit.com")
    print("   - New Python Repl")
    print("   - Upload files and run: python app.py")
    print("   - URL: https://your-repl.repl.co")

def create_test_app():
    """Create a simple test app"""
    test_app = '''from flask import Flask, render_template_string
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
'''
    
    with open('test_app.py', 'w') as f:
        f.write(test_app)
    
    print("Test app created: test_app.py")

if __name__ == '__main__':
    print("MIRROR-X DEPLOYMENT STARTED")
    print("=" * 50)
    
    # Create deployment files
    zip_file = create_deploy_zip()
    create_test_app()
    
    # Print instructions
    deploy_instructions()
    
    print("\n" + "=" * 50)
    print("FILES READY FOR DEPLOYMENT!")
    print("Choose any platform above to deploy live")
    
    # Try to start local server
    print("\nStarting local server...")
    try:
        subprocess.run([sys.executable, 'app.py'], check=True)
    except:
        print("Local server failed - use deployment instructions above")
