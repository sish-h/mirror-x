#!/usr/bin/env python3
"""
MIRROR-X Web Application
Study Intelligence System
"""

from app import app

if __name__ == '__main__':
    print("🪞 MIRROR-X Study Intelligence System")
    print("🚀 Starting web server...")
    print("📊 Open http://localhost:5000 in your browser")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
