# GitHub Push Instructions

Your local repo is ready! To push to GitHub, follow these steps:

## Step 1: Create the remote repository on GitHub
1. Go to https://github.com/new
2. Repository name: `Oddsify Props - MLB`
3. Description: "MLB pitcher strikeout props prediction TUI with real-time odds integration"
4. Choose **Public** (so Oddsify Labs can showcase it)
5. **DO NOT** initialize with README, .gitignore, or LICENSE (we have our own)
6. Click **Create Repository**

## Step 2: Push your local repo
After creating the repo, GitHub will show you commands. Run:

```bash
cd ~/pitcher-ks
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/Oddsify-Props-MLB.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## What's committed:

✅ All source code (main.py, model.py, api_client.py, db.py, config.py)
✅ README.md with full documentation
✅ requirements.txt (dependencies)
✅ run.sh (launcher script)
✅ .gitignore (excludes venv, __pycache__, database)

❌ Excluded: virtual environment, database files, cache

## Commits:

1. **Initial commit** - All project files
2. **.gitignore commit** - Clean repo management

---

Once pushed, share the link:
`https://github.com/YOUR_USERNAME/Oddsify-Props-MLB`

The repo is small (~50KB) and clean, ready for team collaboration!
