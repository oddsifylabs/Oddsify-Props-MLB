# 🪟 Oddsify Props - MLB | Windows Setup Guide

**For Windows 10/11**

---

## Step 1: Install Python (5 minutes)

1. **Download Python**
   - Go to https://www.python.org/downloads/
   - Click "Download Python 3.12" (or latest)
   - Run the installer

2. **Important: Check "Add Python to PATH"**
   - During install, **check the box** at the bottom that says:
     - ☑ "Add python.exe to PATH"
   - Click "Install Now"

3. **Verify Installation**
   - Press `Win+R`
   - Type: `cmd`
   - Press Enter
   - Type: `python --version`
   - You should see: `Python 3.12.x` (or your version)

---

## Step 2: Extract the Project (1 minute)

1. **Download** `oddsify-props-mlb.zip`
2. **Right-click** → Extract All
3. Choose location (e.g., `C:\Users\YourName\oddsify-props-mlb`)
4. Extract

---

## Step 3: Run the App (30 seconds)

### Method A: Double-Click (Easiest)

1. Open the extracted folder
2. Find `run.bat`
3. **Double-click it**
4. Done! App launches automatically

### Method B: Command Prompt (Manual)

1. Press `Win+R`
2. Type: `cmd`
3. Navigate to folder:
   ```
   cd C:\Users\YourName\oddsify-props-mlb\pitcher-ks
   ```
4. Run:
   ```
   python main.py
   ```

---

## 🎮 Using the App

When it launches, you'll see **pitcher strikeouts** for today.

### Controls:
- `0-9` → Click a pitcher for details
- `S` → Settings (bankroll, API key)
- `H` → Bet history
- `R` → Refresh odds
- `Q` → Quit

### First Time Setup:
1. Press `S` for Settings
2. Enter your **bankroll** (e.g., 1000)
3. Enter **API key** from https://www.the-odds-api.com (free)
4. Save & done!

---

## ⚠️ Troubleshooting

### "Python not found"
- **Solution:** Uninstall Python, reinstall with "Add to PATH" **checked**
- Restart Command Prompt after install

### "run.bat doesn't work"
- **Solution:** Right-click → "Run as administrator"
- Or use Command Prompt method above

### "pip install failed"
- **Solution:** Make sure you see `(venv)` in the terminal
- Try: `pip install --upgrade pip` first
- Then: `pip install -r requirements.txt`

### "No props showing"
- **Reason:** Off-season (no MLB games)
- **Solution:** Check if MLB has games today
- Press `R` to refresh
- Make sure API key is set in Settings

### App crashes or won't start
- **Solution:** Delete the database:
  ```
  del C:\Users\YourName\.pitcher-ks\data.db
  ```
- Restart the app

---

## 📁 Folder Structure

After extraction, you'll see:

```
oddsify-props-mlb\
└── pitcher-ks\
    ├── run.bat          ← Double-click to launch
    ├── main.py          ← The app
    ├── model.py         ← Prediction logic
    ├── api_client.py    ← Gets odds data
    ├── db.py            ← Your bets & stats
    ├── config.py        ← Settings
    ├── requirements.txt ← Packages to install
    ├── README.md        ← Full documentation
    └── venv\            ← Created automatically
```

---

## 🔧 Advanced: API Key Setup

The app works with **mock data** (3 sample pitchers) out of the box.

To use **real live odds**:

1. Go to https://www.the-odds-api.com
2. Sign up (free tier = 500 requests/month)
3. Copy your API key
4. Launch the app
5. Press `S` → Settings
6. Paste key in "odds_api_key"
7. Save & restart

That's it! Now you'll get real odds.

---

## ✅ Quick Checklist

- [ ] Python installed & "Add to PATH" checked
- [ ] Folder extracted to C:\Users\YourName\oddsify-props-mlb\
- [ ] Double-clicked run.bat (or ran `python main.py`)
- [ ] App launched successfully
- [ ] Can see pitcher strikeouts
- [ ] Settings accessible (press S)

---

## 🚀 First Time Running

1. **Double-click run.bat**
2. **Wait 5-10 seconds** (first run installs packages)
3. **You should see the app**
4. Press `S` to set bankroll
5. Press `H` to see bet history (empty for now)
6. Click `0-2` to see pitcher details
7. Press `Q` to quit

---

## 💡 Tips for Windows Users

- **Keep it simple:** Just double-click `run.bat` each time
- **Run as Admin:** If you get permission errors, right-click → Run as Administrator
- **Antivirus:** Some antivirus might flag Python/pip. You can whitelist the folder.
- **Firewall:** Make sure firewall allows Python to access the internet (for odds updates)

---

## 📞 Need Help?

- **Can't install Python?** → https://docs.python.org/3/using/windows.html
- **pip not working?** → https://pip.pypa.io/en/stable/installation/
- **API key questions?** → https://www.the-odds-api.com/docs/

---

**Status:** Ready to run ✅  
**Platform:** Windows 10 / 11  
**Created:** July 6, 2026  
**Team:** Oddsify Labs
