# MIRROR-X Deployment Instructions

## Step 1: Prepare Project for Deployment

Files are already configured:
- ✅ `Procfile` created (web: python app.py)
- ✅ `runtime.txt` created (python-3.9.16)
- ✅ `requirements.txt` exists
- ✅ `app.py` configured for production (debug=False, host=0.0.0.0, port=process.env.PORT)

## Step 2: Deploy on Render.com

### Option A: Web Dashboard (Recommended)
1. Go to [render.com](https://render.com)
2. Sign up/login
3. Click "New +" → "Web Service"
4. Connect your GitHub repository OR upload ZIP
5. Configure:
   - **Name**: mirror-x-app
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Instance Type**: Free
6. Click "Create Web Service"

### Option B: Manual ZIP Upload
1. Create ZIP of your project folder
2. Go to render.com → "New +" → "Web Service"
3. Choose "Deploy from ZIP file"
4. Upload your ZIP
5. Use same configuration as above

## Step 3: Deploy on Railway

1. Go to [railway.app](https://railway.app)
2. Sign up/login
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will auto-detect Python
6. Click "Deploy Now"

## Step 4: Deploy on Vercel

1. Go to [vercel.com](https://vercel.com)
2. Sign up/login
3. Click "New Project" → "Import Git Repository"
4. Select your repository
5. Vercel will auto-detect Python
6. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Runtime**: Python 3.9
7. Click "Deploy"

## Step 5: Verify Deployment

After deployment:
1. Wait for build to complete
2. Your app will be available at:
   - Render: `https://your-app-name.onrender.com`
   - Railway: `https://your-app-name.up.railway.app`
   - Vercel: `https://your-app-name.vercel.app`

## Step 6: Test Your App

1. Open your live URL
2. Test signup/login
3. Log a study session
4. Check dashboard and reports
5. Verify all features work

## Troubleshooting

### If build fails:
- Check `requirements.txt` has all dependencies
- Ensure `Procfile` uses correct command
- Verify Python version compatibility

### If app crashes:
- Check logs in deployment dashboard
- Ensure SQLite database permissions
- Verify environment variables

### If static files don't load:
- Check file paths in templates
- Verify CSS is in `/static/` folder
- Check Flask static file configuration

## Database Notes

SQLite works on all platforms:
- ✅ Render: Works (file-based)
- ✅ Railway: Works (file-based)
- ✅ Vercel: Works (read-only file system)

For production, consider PostgreSQL if needed later.

## Next Steps

Your app is now live! Share the URL with users and monitor usage through the platform's analytics dashboard.
