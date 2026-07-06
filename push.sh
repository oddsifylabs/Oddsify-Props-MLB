#!/bin/bash
# Push to GitHub - Run this on any machine with internet access

cd "$(dirname "$0")" || exit 1

echo ""
echo "🚀 Pushing Oddsify Props to GitHub..."
echo ""

# Set remote
git remote add origin https://github.com/oddsifylabs/Oddsify-Props-MLB.git 2>/dev/null || \
  git remote set-url origin https://github.com/oddsifylabs/Oddsify-Props-MLB.git

# Ensure main branch
git branch -M main

# Push
echo "📤 Pushing commits to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS!"
    echo ""
    echo "Your repo is live at:"
    echo "   https://github.com/oddsifylabs/Oddsify-Props-MLB"
    echo ""
    echo "Recent commits:"
    git log --oneline -3
    echo ""
else
    echo "❌ Push failed. Check your internet connection and GitHub credentials."
    exit 1
fi
