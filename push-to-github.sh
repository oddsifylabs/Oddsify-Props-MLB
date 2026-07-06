#!/bin/bash
# Auto-push Oddsify Props to GitHub
# Run this on any machine with git installed

set -e  # Exit on error

echo "🚀 Oddsify Props - MLB | GitHub Auto-Push"
echo "==========================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Install from https://git-scm.com"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "requirements.txt" ] || [ ! -f "main.py" ]; then
    echo "❌ Error: Not in pitcher-ks directory"
    echo "   Run: cd pitcher-ks && bash push-to-github.sh"
    exit 1
fi

echo "✅ Found pitcher-ks project"
echo ""

# Configure git
echo "📝 Configuring git..."
git config user.name "Oddsify Labs" || true
git config user.email "jesse@oddsifylabs.com" || true

# Initialize if needed
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git branch -M main
fi

# Add files
echo "📥 Staging files..."
git add .

# Check if there's anything to commit
if git diff --cached --quiet; then
    echo "✅ No changes to commit (repo already pushed)"
    exit 0
fi

# Create commit
echo "💾 Creating commit..."
git commit -m "Initial commit: Pitcher K's MLB strikeout model TUI app" || true

# Check remote
if ! git remote get-url origin &> /dev/null; then
    echo ""
    echo "🔗 Setting up GitHub remote..."
    git remote add origin https://github.com/oddsifylabs/Oddsify-Props-MLB.git
fi

# Push
echo ""
echo "🚀 Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ SUCCESS!"
echo ""
echo "Your repo is live at:"
echo "   https://github.com/oddsifylabs/Oddsify-Props-MLB"
echo ""
echo "Share this link with your team:"
echo "   git clone https://github.com/oddsifylabs/Oddsify-Props-MLB"
echo ""
