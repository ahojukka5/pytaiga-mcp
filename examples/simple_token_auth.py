#!/usr/bin/env python3
"""
Simple example: Authenticate with Taiga using Application Token

This is the EASIEST and MOST SECURE way to authenticate!

Steps:
1. Get Application Token from Taiga (Settings → Applications)
2. Add to .env file or export as environment variable
3. Run this script

No passwords, no caching, just simple token authentication.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

from pytaiga_mcp.server.auth import login_with_token
from pytaiga_mcp.server.projects import list_projects


def main():
    """Simple example of Application Token authentication."""

    # Load environment variables from .env file
    load_dotenv()

    # Get token from environment
    host = os.getenv("TAIGA_HOST", "https://api.taiga.io")
    auth_token = os.getenv("TAIGA_AUTH_TOKEN")
    token_type = os.getenv("TAIGA_TOKEN_TYPE", "Application")

    if not auth_token:
        print("❌ Error: TAIGA_AUTH_TOKEN not found in environment")
        print("\n" + "=" * 70)
        print("📖 HOW TO GET YOUR APPLICATION TOKEN FROM TAIGA")
        print("=" * 70)
        print("\n🌐 Step 1: Login to Taiga Web Interface")
        print("   • Open your browser and go to: https://tree.taiga.io")
        print("     (or your company's Taiga URL if self-hosted)")
        print("   • Login with your username and password")
        print("\n👤 Step 2: Go to User Settings")
        print("   • Click on your profile icon/avatar (top-right corner)")
        print("   • Select 'Settings' from the dropdown menu")
        print("\n🔑 Step 3: Navigate to Applications Section")
        print("   • In the left sidebar, look for 'Applications' or 'API Tokens'")
        print("   • Click on it")
        print("\n✨ Step 4: Create a New Application Token")
        print("   • Click the button: 'Create new application' or 'Generate Token'")
        print("   • Give it a name, for example:")
        print("     - 'MCP Integration'")
        print("     - 'Development Token'")
        print("     - 'My Computer'")
        print("   • Click 'Create' or 'Generate'")
        print("\n📋 Step 5: Copy the Token")
        print("   • A long token will appear (looks like: eyJ0eXAiOiJKV1Qi...)")
        print("   • Copy it immediately - you won't see it again!")
        print("   • ⚠️  Important: Keep this token secret, like a password")
        print("\n💾 Step 6: Save Token to .env File")
        print("   • Create or edit the .env file in this project's root directory")
        print("   • Add these lines:")
        print("\n   TAIGA_HOST=https://api.taiga.io")
        print("   TAIGA_AUTH_TOKEN=paste_your_token_here")
        print("   TAIGA_TOKEN_TYPE=Application")
        print("\n   • Replace 'paste_your_token_here' with the actual token you copied")
        print("\n🚀 Step 7: Run This Script Again")
        print("   • Save the .env file")
        print("   • Run: python examples/simple_token_auth.py")
        print("\n" + "=" * 70)
        print("\n💡 Alternative: Use Environment Variable (Temporary)")
        print("   export TAIGA_AUTH_TOKEN='your_token_here'")
        print("   python examples/simple_token_auth.py")
        print("\n⚠️  Security Reminder:")
        print("   • Never commit .env file to git (add it to .gitignore)")
        print("   • Never share your token publicly")
        print("   • You can revoke tokens anytime in Taiga Settings → Applications")
        print("\n📚 Need more help? See: QUICKSTART.md or TOKEN_AUTH_GUIDE.md")
        print("=" * 70)
        sys.exit(1)

    print(f"🔐 Authenticating with Taiga at {host}...")
    print(f"   Token type: {token_type}")
    print(f"   Token: {auth_token[:20]}..." if len(auth_token) > 20 else f"   Token: {auth_token}")

    try:
        # Login with Application Token
        result = login_with_token(host=host, auth_token=auth_token, token_type=token_type)

        session_id = result["session_id"]
        print("✅ Authentication successful!")
        print(f"   Session ID: {session_id}")

        # Test: List projects
        print("\n📋 Fetching your projects...")
        projects_result = list_projects(session_id=session_id)
        projects = projects_result.get("projects", [])

        if projects:
            print(f"✅ Found {len(projects)} project(s):")
            for i, project in enumerate(projects, 1):
                print(f"   {i}. {project['name']} (ID: {project['id']})")
                if project.get("description"):
                    print(f"      {project['description'][:60]}...")
        else:
            print("ℹ️  No projects found. Create one in Taiga web interface!")

        print("\n✨ Success! You're authenticated and ready to use the Taiga MCP bridge.")
        print("\n💡 Tips:")
        print("   - This token can be reused forever (until revoked)")
        print("   - No password storage needed")
        print("   - Revoke anytime in Taiga Settings → Applications")
        print("   - Generate new tokens for different environments (dev/prod)")

    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        print("\n🔍 Troubleshooting:")
        print("   - Check if token is correct (no extra spaces)")
        print("   - Verify token hasn't been revoked in Taiga")
        print("   - Confirm host URL is correct")
        print("   - Try generating a new token")
        sys.exit(1)


if __name__ == "__main__":
    main()
