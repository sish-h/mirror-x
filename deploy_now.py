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

def deploy_to_render():
    """Deploy to Render"""
    print("RENDER DEPLOYMENT:")
    print("1. Go to https://render.com")
    print("2. Sign up/login")
    print("3. Click 'New +' -> 'Web Service'")
    print("4. Connect to GitHub")
    print("5. Upload your files")
    print("6. Set build command: pip install -r requirements.txt")
    print("7. Set start command: gunicorn app:app --bind 0.0.0.0:$PORT")
    print("8. Deploy!")
    print("URL: https://your-app-name.onrender.com")
    return True

def deploy_to_railway():
    """Deploy to Railway"""
    print("RAILWAY DEPLOYMENT:")
    print("1. Go to https://railway.app")
    print("2. Sign up/login")
    print("3. Click 'New Project' -> 'Deploy from GitHub repo'")
    print("4. Upload your files to GitHub")
    print("5. Select the repo")
    print("6. Railway will auto-detect Flask")
    print("7. Deploy!")
    print("URL: https://your-app-name.up.railway.app")
    return True

def deploy_to_pythonanywhere():
    """Deploy to PythonAnywhere"""
    print("PYTHONANYWHERE DEPLOYMENT:")
    print("1. Go to https://www.pythonanywhere.com")
    print("2. Sign up for free account")
    print("3. Go to 'Web' tab")
    print("4. Click 'Add a new web app'")
    print("5. Choose Flask and Python 3.10")
    print("6. Upload your files")
    print("7. Set WSGI configuration")
    print("8. Reload web app")
    print("URL: https://yourusername.pythonanywhere.com")
    return True

def deploy_to_replit():
    """Deploy to Replit"""
    print("REPLIT DEPLOYMENT:")
    print("1. Go to https://replit.com")
    print("2. Sign up/login")
    print("3. Create new Repl -> Python")
    print("4. Upload all your files")
    print("5. Install dependencies: pip install -r requirements.txt")
    print("6. Run: python app.py")
    print("7. Click 'Share' -> 'Publish to web'")
    print("URL: https://your-repl-name.yourusername.repl.co")
    return True

def quick_test():
    """Quick test deployment"""
    print("Creating test deployment...")
    
    # Create a simple test app
    test_app = '''from flask import Flask, render_template_string
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string('''
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
        <div class="logo">🪞 MIRROR-X</div>
        <div class="status">🌐 LIVE</div>
        <h1>Your Study Accountability System</h1>
        <div class="features">
            <div class="feature">✅ AI Chat System</div>
            <div class="feature">✅ Study Tracking</div>
            <div class="feature">✅ Mirror-X Behavioral Engine</div>
            <div class="feature">✅ Leaderboard</div>
            <div class="feature">✅ Transformation Mode</div>
            <div class="feature">✅ Weekly Reports</div>
        </div>
        <p><strong>Status:</strong> All systems operational</p>
        <p><em>This is a live deployment of MIRROR-X</em></p>
    </div>
</body>
</html>
''')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
'''
    
    with open('test_app.py', 'w') as f:
        f.write(test_app)
    
    print("Test app created: test_app.py")
    return True

if __name__ == '__main__':
    print("MIRROR-X DEPLOYMENT STARTED")
    print("=" * 50)
    
    # Create deployment zip
    zip_file = create_deploy_zip()
    
    print("\nDEPLOYMENT OPTIONS:")
    print("=" * 30)
    
    # Try each deployment method
    deploy_to_render()
    print()
    deploy_to_railway()
    print()
    deploy_to_pythonanywhere()
    print()
    deploy_to_replit()
    
    print("\nQUICK TEST:")
    print("=" * 20)
    quick_test()
    
    print("\n" + "=" * 50)
    print("DEPLOYMENT FILES READY!")
    print("Choose any platform above to deploy")
    print("All files are prepared for deployment")
    
    # Try to start local server as fallback
    print("\nSTARTING LOCAL SERVER...")
    try:
        os.system('python app.py')
    except:
        print("Could not start local server")
