"""
GitHub OAuth authentication for Taiga MCP Bridge.

Implements GitHub OAuth flow to authenticate with Taiga using GitHub account.
"""

import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Event, Thread
from urllib.parse import parse_qs, urlparse

import httpx


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback from GitHub."""

    auth_code: str | None = None
    auth_error: str | None = None
    done_event: Event = Event()

    def do_GET(self):
        """Handle GET request from OAuth redirect."""
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)

        if "code" in query_params:
            OAuthCallbackHandler.auth_code = query_params["code"][0]
            self.send_success_response()
        elif "error" in query_params:
            OAuthCallbackHandler.auth_error = query_params.get(
                "error_description", ["Unknown error"]
            )[0]
            self.send_error_response()
        else:
            self.send_error_response("Invalid callback")

        OAuthCallbackHandler.done_event.set()

    def send_success_response(self):
        """Send success HTML response."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentication Successful</title>
            <style>
                body {
                    font-family: system-ui, -apple-system, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }
                .card {
                    background: white;
                    padding: 3rem;
                    border-radius: 1rem;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    text-align: center;
                    max-width: 500px;
                }
                .success {
                    color: #10b981;
                    font-size: 4rem;
                    margin-bottom: 1rem;
                }
                h1 {
                    color: #1f2937;
                    margin-bottom: 0.5rem;
                }
                p {
                    color: #6b7280;
                    line-height: 1.6;
                }
            </style>
        </head>
        <body>
            <div class="card">
                <div class="success">✓</div>
                <h1>Authentication Successful!</h1>
                <p>You have been successfully authenticated with GitHub.</p>
                <p>You can now close this window and return to your terminal.</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

    def send_error_response(self, error_message: str = "Authentication failed"):
        """Send error HTML response."""
        self.send_response(400)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentication Failed</title>
            <style>
                body {{
                    font-family: system-ui, -apple-system, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #f87171 0%, #dc2626 100%);
                }}
                .card {{
                    background: white;
                    padding: 3rem;
                    border-radius: 1rem;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    text-align: center;
                    max-width: 500px;
                }}
                .error {{
                    color: #ef4444;
                    font-size: 4rem;
                    margin-bottom: 1rem;
                }}
                h1 {{
                    color: #1f2937;
                    margin-bottom: 0.5rem;
                }}
                p {{
                    color: #6b7280;
                    line-height: 1.6;
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="error">✗</div>
                <h1>Authentication Failed</h1>
                <p>{error_message}</p>
                <p>Please try again or contact support if the problem persists.</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        """Suppress HTTP server log messages."""
        pass


def get_github_auth_code(redirect_uri: str = "http://localhost:8765/callback") -> str:
    """
    Start OAuth flow and wait for authorization code.

    This function:
    1. Starts a local HTTP server to receive the callback
    2. Opens browser for GitHub authorization
    3. Waits for user to authorize
    4. Returns the authorization code

    Args:
        redirect_uri: Local URI for OAuth callback

    Returns:
        GitHub authorization code

    Raises:
        RuntimeError: If authorization fails or times out
    """
    # Reset class variables
    OAuthCallbackHandler.auth_code = None
    OAuthCallbackHandler.auth_error = None
    OAuthCallbackHandler.done_event = Event()

    # Start local server
    port = int(urlparse(redirect_uri).port or 8765)
    server = HTTPServer(("localhost", port), OAuthCallbackHandler)

    def run_server():
        while not OAuthCallbackHandler.done_event.is_set():
            server.handle_request()

    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()

    # GitHub OAuth URL - using Taiga's GitHub OAuth app
    # For public Taiga instance (api.taiga.io), there's a configured GitHub OAuth app
    # For self-hosted instances, you need to configure your own GitHub OAuth app
    # See: https://docs.taiga.io/setup-production.html#github-oauth
    print()
    print("=" * 70)
    print("⚠️  IMPORTANT: GitHub OAuth Setup Required")
    print("=" * 70)
    print()
    print("To use GitHub authentication, you need:")
    print()
    print("1. A GitHub OAuth App configured for your Taiga instance")
    print("2. The GitHub Client ID from that OAuth app")
    print()
    print("For api.taiga.io:")
    print("  - Taiga.io should have a pre-configured GitHub OAuth app")
    print("  - If this doesn't work, contact Taiga support")
    print()
    print("For self-hosted Taiga:")
    print("  - Create a GitHub OAuth app at: https://github.com/settings/developers")
    print("  - Set Authorization callback URL to: http://localhost:8765/callback")
    print("  - Configure Taiga with your GitHub OAuth app credentials")
    print("  - See: https://docs.taiga.io/setup-production.html#github-oauth")
    print()
    print("=" * 70)
    print()

    github_client_id = input("Enter GitHub OAuth Client ID: ").strip()
    if not github_client_id:
        raise RuntimeError("GitHub Client ID is required")

    # Build GitHub OAuth URL
    github_auth_url = (
        "https://github.com/login/oauth/authorize?"
        f"client_id={github_client_id}&"
        f"redirect_uri={redirect_uri}&"
        "scope=user:email"
    )

    print()
    print("Opening browser for GitHub authorization...")
    print(f"If browser doesn't open, visit: {github_auth_url}")
    print()
    print("Waiting for authorization...")

    try:
        webbrowser.open(github_auth_url)
    except Exception as e:
        print(f"Warning: Could not open browser automatically: {e}", file=sys.stderr)
        print(f"Please visit: {github_auth_url}")

    # Wait for callback with timeout
    if not OAuthCallbackHandler.done_event.wait(timeout=300):  # 5 minutes
        raise RuntimeError("Authorization timeout. Please try again.")

    server.shutdown()

    if OAuthCallbackHandler.auth_error:
        raise RuntimeError(f"Authorization failed: {OAuthCallbackHandler.auth_error}")

    if not OAuthCallbackHandler.auth_code:
        raise RuntimeError("No authorization code received")

    return OAuthCallbackHandler.auth_code  # type: ignore[unreachable]


def login_with_github(api_url: str, github_code: str) -> dict:
    """
    Exchange GitHub code for Taiga authentication token.

    Args:
        api_url: Taiga API URL (e.g., https://api.taiga.io)
        github_code: GitHub authorization code

    Returns:
        Dictionary with auth_token and user info

    Raises:
        httpx.HTTPError: If authentication fails
    """
    # Ensure API URL doesn't end with /api/v1
    api_url = api_url.rstrip("/")
    if api_url.endswith("/api/v1"):
        api_url = api_url[:-7]

    login_url = f"{api_url}/api/v1/auth"

    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            login_url,
            json={"type": "github", "code": github_code},
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return response.json()


def github_oauth_flow(api_url: str, env_path: Path) -> None:
    """
    Complete GitHub OAuth authentication flow.

    Args:
        api_url: Taiga API URL
        env_path: Path to save .env file

    Raises:
        RuntimeError: If authentication fails
        httpx.HTTPError: If API communication fails
    """
    print("=" * 70)
    print("Taiga MCP Bridge - GitHub Authentication")
    print("=" * 70)
    print()
    print("This will authenticate you with Taiga using your GitHub account.")
    print()

    # Get authorization code
    try:
        github_code = get_github_auth_code()
        print("\n✓ GitHub authorization received")
    except Exception as e:
        print(f"\n✗ GitHub authorization failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Exchange code for Taiga token
    print("Authenticating with Taiga...")

    try:
        auth_data = login_with_github(api_url, github_code)
        auth_token = auth_data.get("auth_token")

        if not auth_token:
            print("\n✗ No auth token received from Taiga", file=sys.stderr)
            sys.exit(1)

        # Create .env file (import from auth_setup)
        from pytaiga_mcp.auth_setup import create_env_file

        create_env_file(api_url, auth_token, env_path)

        print("\n✓ Authentication successful!")
        print(f"✓ Created {env_path.absolute()}")
        print()
        print("You can now run: poetry run pytaiga-mcp")
        print()

    except httpx.HTTPStatusError as e:
        print(f"\n✗ Authentication failed: {e.response.status_code}", file=sys.stderr)
        if e.response.status_code == 400:
            print(
                "  Invalid GitHub code or Taiga not configured for GitHub OAuth.",
                file=sys.stderr,
            )
        print(f"  Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except httpx.HTTPError as e:
        print(f"\n✗ Network error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def github_oauth_to_cache(host: str) -> tuple[str, int] | None:
    """
    GitHub OAuth flow that returns token for caching.

    Args:
        host: Taiga host URL

    Returns:
        Tuple of (auth_token, user_id) or None if failed
    """
    print("=" * 70)
    print("Taiga MCP Bridge - GitHub Authentication")
    print("=" * 70)
    print()
    print(f"Host: {host}")
    print()
    print("This will authenticate you with Taiga using your GitHub account.")
    print()

    # Get authorization code
    try:
        github_code = get_github_auth_code()
        print("\n✓ GitHub authorization received")
    except Exception as e:
        print(f"\n✗ GitHub authorization failed: {e}", file=sys.stderr)
        return None

    # Exchange code for Taiga token
    print("Authenticating with Taiga...")

    try:
        auth_data = login_with_github(host, github_code)
        auth_token = auth_data.get("auth_token")
        user_id = auth_data.get("id")

        if not auth_token or not isinstance(auth_token, str):
            print("\n✗ No auth token received from Taiga", file=sys.stderr)
            return None

        if not user_id or not isinstance(user_id, int):
            print("\n✗ No valid user ID received from Taiga", file=sys.stderr)
            return None

        print("\n✓ Authentication successful!")
        return (auth_token, user_id)

    except httpx.HTTPStatusError as e:
        print(f"\n✗ Authentication failed: {e.response.status_code}", file=sys.stderr)
        if e.response.status_code == 400:
            print(
                "  Invalid GitHub code or Taiga not configured for GitHub OAuth.",
                file=sys.stderr,
            )
        print(f"  Response: {e.response.text}", file=sys.stderr)
        return None
    except httpx.HTTPError as e:
        print(f"\n✗ Network error: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}", file=sys.stderr)
        return None
