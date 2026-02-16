# MIRROR-X - Quick Deploy Guide

## 🚀 One-Click Deployment Options

### Option 1: Render (Easiest)
```bash
# 1. Push to GitHub
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Go to render.com → New Web Service
# 3. Connect your GitHub repo
# 4. Auto-deploy with settings below
```

### Option 2: Railway
```bash
# 1. Push to GitHub
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Go to railway.app → New Project from GitHub
# 3. Select repo and deploy
```

### Option 3: Vercel
```bash
# 1. Push to GitHub
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Go to vercel.com → Import Git Repository
# 3. Select repo and deploy
```

## 📋 Required Files (Already Created)

- `Procfile` - Tells platform how to run your app
- `runtime.txt` - Specifies Python version
- `requirements.txt` - Dependencies
- `app.py` - Production-ready Flask app

## ⚙️ Deployment Settings

**Build Command**: `pip install -r requirements.txt`
**Start Command**: `python app.py`
**Runtime**: Python 3.9
**Port**: 5000 (auto-assigned by platform)

## 🔧 Quick Test Local

```bash
# Test production mode locally
export PORT=5000
python app.py
```

## 🌐 Live URL Examples

- Render: `https://mirror-x.onrender.com`
- Railway: `https://mirror-x.up.railway.app`
- Vercel: `https://mirror-x.vercel.app`

## ✅ Pre-Deployment Checklist

- [ ] All files committed to Git
- [ ] Requirements.txt includes Flask, pandas, matplotlib
- [ ] Procfile exists with `web: python app.py`
- [ ] Runtime.txt specifies Python 3.9.16
- [ ] App runs with `debug=False`
- [ ] Static files in `/static/` folder
- [ ] Templates in `/templates/` folder

## 🚨 Common Issues

**Issue**: Build fails
**Fix**: Check Python version in runtime.txt

**Issue**: Database errors
**Fix**: SQLite works out-of-the-box

**Issue**: CSS not loading
**Fix**: Check `/static/` folder structure

## 🎉 Success!

Your MIRROR-X app is now live and accessible worldwide!
