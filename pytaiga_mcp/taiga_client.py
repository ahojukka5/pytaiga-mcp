"""
Taiga API client wrapper for managing authentication and API access.

This module provides a high-level wrapper around pytaigaclient that handles:
- Username/password authentication
- Token-based authentication (Bearer and Application tokens)
- Session state management
- User information caching

Example:
    ```python
    from taiga_client import TaigaClientWrapper

    # Initialize client
    client = TaigaClientWrapper(host="https://tree.taiga.io")

    # Authenticate with token (recommended)
    client.login_with_token(auth_token="your-app-token", token_type="Application")

    # Or authenticate with username/password (deprecated)
    client.login(username="user", password="pass")

    # Use the API
    if client.is_authenticated:
        projects = client.api.projects.list()
    ```
"""

import logging

from pytaigaclient import TaigaClient
from pytaigaclient.exceptions import TaigaException

logger = logging.getLogger(__name__)


class TaigaClientWrapper:
    """
    Wrapper for pytaigaclient that manages authentication state and API access.

    This class provides a simplified interface for authenticating with Taiga and
    maintaining the API client instance. It supports both username/password and
    token-based authentication methods.

    Attributes:
        host: The base URL of the Taiga instance (e.g., 'https://tree.taiga.io')
        api: The pytaigaclient TaigaClient instance (None if not authenticated)
        user_id: The authenticated user's ID (None if not authenticated)
        username: The authenticated user's username (None if not authenticated)

    Note:
        Token-based authentication is recommended over username/password for
        security and simplicity. Application tokens are preferred over Bearer tokens.
    """

    def __init__(self, host: str):
        """
        Initialize the Taiga client wrapper.

        Args:
            host: The base URL of the Taiga instance (e.g., 'https://tree.taiga.io')
                 Must be a valid HTTP/HTTPS URL.

        Raises:
            ValueError: If host is empty or None

        Note:
            The API client is not initialized until authentication occurs via
            either login() or login_with_token().
        """
        if not host:
            raise ValueError("Taiga host URL cannot be empty.")

        self.host = host
        self.api: TaigaClient | None = None
        self.user_id: int | None = None
        self.username: str | None = None

        logger.info(f"TaigaClientWrapper initialized for host: {self.host}")

    def login(self, username: str, password: str) -> bool:
        """
        Authenticate with Taiga using username and password.

        **DEPRECATED**: Use login_with_token() instead for better security.
        This method stores credentials temporarily but exposes them in memory.
        Consider using Application Tokens for authentication.

        Args:
            username: The Taiga username or email address
            password: The Taiga password

        Returns:
            True if authentication succeeds

        Raises:
            TaigaException: If authentication fails due to invalid credentials
                           or network errors
            ValueError: If username or password is empty

        Example:
            ```python
            client = TaigaClientWrapper(host="https://tree.taiga.io")
            try:
                client.login(username="myuser", password="mypass")
                print(f"Logged in as {client.username}")
            except TaigaException as e:
                print(f"Login failed: {e}")
            ```

        Note:
            On successful login, the api, user_id, and username attributes
            are populated. The auth token is stored in the API client for
            subsequent requests.
        """
        try:
            logger.info(f"Attempting login for user '{username}' on {self.host}")

            api_instance = TaigaClient(host=self.host)
            auth_response = api_instance.auth.login(username=username, password=password)
            self.api = api_instance

            if isinstance(auth_response, dict):
                self.user_id = auth_response.get("id")
                self.username = auth_response.get("username", username)
                logger.info(
                    f"Login successful for user '{username}' (ID: {self.user_id}). Auth token acquired."
                )
            else:
                logger.warning("Login response didn't contain expected user information")
                logger.info(f"Login successful for user '{username}'. Auth token acquired.")

            return True

        except TaigaException as e:
            logger.error(f"Taiga login failed for user '{username}': {e}", exc_info=False)
            self.api = None
            self.user_id = None
            self.username = None
            raise e
        except Exception as e:
            logger.error(
                f"An unexpected error occurred during login for user '{username}': {e}",
                exc_info=True,
            )
            self.api = None
            self.user_id = None
            self.username = None
            raise TaigaException(f"Unexpected login error: {e}")

    def login_with_token(
        self, auth_token: str, token_type: str = "Bearer", user_id: int | None = None
    ) -> bool:
        """
        Authenticate with Taiga using an authentication token.

        **RECOMMENDED**: This is the preferred authentication method as it doesn't
        require storing passwords. Application tokens are especially recommended
        as they can have limited scopes and be easily revoked.

        Args:
            auth_token: The authentication token obtained from Taiga
            token_type: Type of token - "Bearer" (session token) or "Application"
                       (recommended). Defaults to "Bearer".
            user_id: Optional user ID if known. If not provided, will be fetched
                    from the /users/me endpoint.

        Returns:
            True if authentication succeeds

        Raises:
            TaigaException: If authentication fails due to invalid token or
                           network errors

        Example:
            ```python
            client = TaigaClientWrapper(host="https://tree.taiga.io")

            # Application token (recommended)
            client.login_with_token(
                auth_token="your-application-token",
                token_type="Application"
            )

            # Or Bearer token (session token)
            client.login_with_token(
                auth_token="your-bearer-token",
                token_type="Bearer",
                user_id=12345
            )
            ```

        Note:
            - Application tokens are obtained from User Settings -> Application Tokens
            - Bearer tokens are session tokens from login responses
            - If user_id is not provided, an API call is made to fetch user info
            - On success, api, user_id, and username attributes are populated
        """
        try:
            logger.info(f"Attempting token authentication on {self.host}")

            self.api = TaigaClient(host=self.host, auth_token=auth_token, token_type=token_type)

            if user_id is not None:
                self.user_id = user_id
                logger.info(f"Token authentication successful (User ID: {self.user_id})")
            else:
                try:
                    user_info = self.api.users.get_me()
                    if isinstance(user_info, dict):
                        self.user_id = user_info.get("id")
                        self.username = user_info.get("username")
                        logger.info(
                            f"Token authentication successful for user '{self.username}' (ID: {self.user_id})"
                        )
                    else:
                        logger.warning("Could not fetch user info, continuing without user_id")
                        logger.info("Token authentication successful")
                except Exception as e:
                    logger.warning(f"Could not fetch user info: {e}")
                    logger.info("Token authentication successful (user info unavailable)")

            return True

        except TaigaException as e:
            logger.error(f"Token authentication failed: {e}", exc_info=False)
            self.api = None
            self.user_id = None
            self.username = None
            raise e
        except Exception as e:
            logger.error(f"Unexpected error during token authentication: {e}", exc_info=True)
            self.api = None
            self.user_id = None
            self.username = None
            raise TaigaException(f"Unexpected token authentication error: {e}")

    @property
    def is_authenticated(self) -> bool:
        """
        Check if the client is currently authenticated.

        Returns:
            True if the client has a valid API instance with an auth token,
            False otherwise.

        Example:
            ```python
            if client.is_authenticated:
                projects = client.api.projects.list()
            else:
                print("Please login first")
            ```
        """
        return self.api is not None and self.api.auth_token is not None

    def _ensure_authenticated(self) -> None:
        """
        Internal helper to verify authentication before API operations.

        Raises:
            PermissionError: If the client is not authenticated

        Note:
            This method is typically called internally before API operations
            that require authentication. It's not necessary to call this
            directly as authenticated operations will check automatically.
        """
        if not self.is_authenticated:
            logger.error("Action required authentication, but client is not logged in.")
            raise PermissionError("Client not authenticated. Please login first.")
