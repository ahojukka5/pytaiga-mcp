#!/usr/bin/env python3
"""
Example: Secure Authentication Workflow
Demonstrates the recommended way to authenticate with Taiga MCP server.
"""

import os
from pytaiga_mcp.server.auth import (
    login,
    login_from_cache,
    save_session_token,
    login_with_token,
    list_cached_tokens_tool,
    delete_cached_token,
    logout,
)


def example_first_time_setup():
    """
    First-time setup: Login with password and save token.
    This should only be done ONCE, then password can be removed.
    """
    print("=" * 60)
    print("FIRST TIME SETUP")
    print("=" * 60)

    # Step 1: Login with username/password (first time only)
    print("\n1. Logging in with username/password...")
    result = login(
        host="https://api.taiga.io",
        username="your_username",  # Replace with your username
        password="your_password",  # Replace with your password
    )

    if "session_id" not in result:
        print("❌ Login failed!")
        return None

    session_id = result["session_id"]
    print(f"✅ Login successful! Session ID: {session_id[:8]}...")

    # Step 2: Save the token to cache
    print("\n2. Saving authentication token to cache...")
    save_result = save_session_token(session_id)

    if save_result["status"] == "success":
        print(f"✅ Token saved successfully!")
        print(f"   Cache location: {save_result.get('cache_location', 'N/A')}")
        print(f"   User ID: {save_result.get('user_id')}")
    else:
        print(f"❌ Failed to save token: {save_result.get('message')}")
        return None

    # Step 3: Cleanup - logout from this session
    print("\n3. Logging out...")
    logout(session_id)
    print("✅ Logged out")

    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("You can now:")
    print("  1. DELETE YOUR PASSWORD from config files")
    print("  2. Use login_from_cache() for future authentications")
    print("=" * 60)

    return True


def example_secure_login():
    """
    Recommended: Login using cached token (no password needed).
    """
    print("\n" + "=" * 60)
    print("SECURE LOGIN (No Password Required)")
    print("=" * 60)

    # Login using cached token
    print("\n1. Logging in from cache...")
    result = login_from_cache(host="https://api.taiga.io")

    if "session_id" not in result:
        print(f"❌ Login failed: {result.get('message')}")
        print("   You may need to run first-time setup.")
        return None

    session_id = result["session_id"]
    print(f"✅ Login successful! Session ID: {session_id[:8]}...")
    print("   No password was used! Token was loaded from cache.")

    return session_id


def example_application_token():
    """
    Most secure: Use Application Token from Taiga web interface.
    """
    print("\n" + "=" * 60)
    print("APPLICATION TOKEN LOGIN (Most Secure)")
    print("=" * 60)

    print("\n1. Get your application token:")
    print("   - Go to Taiga web interface")
    print("   - User Settings → Applications")
    print("   - Create new application")
    print("   - Copy the generated token")

    # You would store this in environment variable
    app_token = os.getenv("TAIGA_APPLICATION_TOKEN")

    if not app_token:
        print("\n⚠️  TAIGA_APPLICATION_TOKEN not set in environment")
        print("   Set it with: export TAIGA_APPLICATION_TOKEN='your_token_here'")
        return None

    print("\n2. Logging in with application token...")
    result = login_with_token(
        host="https://api.taiga.io", auth_token=app_token, token_type="Application"
    )

    if "session_id" not in result:
        print(f"❌ Login failed: {result.get('message')}")
        return None

    session_id = result["session_id"]
    print(f"✅ Login successful! Session ID: {session_id[:8]}...")

    return session_id


def example_manage_tokens():
    """
    Demonstrate token management operations.
    """
    print("\n" + "=" * 60)
    print("TOKEN MANAGEMENT")
    print("=" * 60)

    # List all cached tokens
    print("\n1. Listing cached tokens...")
    result = list_cached_tokens_tool()

    if result["count"] == 0:
        print("   No cached tokens found")
    else:
        print(f"   Found {result['count']} cached token(s):")
        for host, info in result["tokens"].items():
            print(f"   - {host}")
            print(f"     Type: {info['token_type']}")
            print(f"     User ID: {info['user_id']}")

    # Delete a token (example)
    # Uncomment to actually delete:
    # print("\n2. Deleting cached token...")
    # delete_result = delete_cached_token("https://api.taiga.io")
    # print(f"   Status: {delete_result['status']}")


def main():
    """Main example runner."""
    print("\n" + "=" * 60)
    print("TAIGA MCP - SECURE AUTHENTICATION EXAMPLES")
    print("=" * 60)

    print("\nThis script demonstrates three authentication methods:")
    print("  1. First-time setup (with password - only once)")
    print("  2. Secure login from cache (recommended)")
    print("  3. Application token login (most secure)")
    print("  4. Token management")

    # Show which example to run
    print("\n" + "=" * 60)
    print("CHOOSE AN EXAMPLE:")
    print("=" * 60)
    print("1. Run first-time setup (saves token)")
    print("2. Run secure login from cache")
    print("3. Run application token login")
    print("4. Manage cached tokens")
    print("5. Run all examples (except first-time setup)")

    choice = input("\nEnter choice (1-5): ").strip()

    if choice == "1":
        example_first_time_setup()
    elif choice == "2":
        example_secure_login()
    elif choice == "3":
        example_application_token()
    elif choice == "4":
        example_manage_tokens()
    elif choice == "5":
        example_secure_login()
        example_application_token()
        example_manage_tokens()
    else:
        print("Invalid choice!")

    print("\n" + "=" * 60)
    print("SECURITY REMINDER:")
    print("=" * 60)
    print("✅ DO: Use token-based authentication")
    print("✅ DO: Store tokens in secure cache (~/.cache/taiga-mcp/)")
    print("✅ DO: Use environment variables for production")
    print("❌ DON'T: Store passwords in .env files")
    print("❌ DON'T: Commit passwords to version control")
    print("❌ DON'T: Hardcode credentials in code")
    print("=" * 60)


if __name__ == "__main__":
    # Note: This is a demonstration script
    # In practice, you would import and use these functions in your application
    print("\n⚠️  NOTE: This is a demonstration script")
    print("   Update the username/password/token values before running")
    print("   Or use it as a reference for your own code")

    # Uncomment to run:
    # main()

    print("\nTo use in production:")
    print("  1. Run first-time setup with real credentials")
    print("  2. Delete password from config")
    print("  3. Use login_from_cache() for all future logins")
