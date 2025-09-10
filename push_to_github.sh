#!/bin/bash

echo "🚀 Pushing SimpleIQ to GitHub..."
echo ""
echo "Please choose your authentication method:"
echo "1) GitHub CLI (recommended)"
echo "2) SSH (if you have SSH keys set up)"
echo "3) Personal Access Token"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "Using GitHub CLI..."
        gh auth login
        gh repo create simpleiq --public --source=. --remote=origin --push
        ;;
    2)
        echo "Switching to SSH..."
        git remote set-url origin git@github.com:kojjob/simpleiq.git
        git push -u origin main
        git push -u origin develop
        ;;
    3)
        echo "Please create a Personal Access Token at:"
        echo "https://github.com/settings/tokens"
        echo ""
        read -p "Enter your GitHub username: " username
        read -s -p "Enter your Personal Access Token: " token
        echo ""
        git push https://$username:$token@github.com/kojjob/simpleiq.git main
        git push https://$username:$token@github.com/kojjob/simpleiq.git develop
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "✅ Done! Your repository should now be available at:"
echo "https://github.com/kojjob/simpleiq"