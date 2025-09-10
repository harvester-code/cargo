import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import logging

# Suppress streamlit-authenticator debug output
logging.getLogger("streamlit_authenticator").setLevel(logging.WARNING)


class AuthenticationManager:
    """Cargo Analysis Dashboard Authentication Manager Class"""

    def __init__(self, config_path="config.yaml"):
        """
        Initialize Authentication Manager

        Args:
            config_path (str): Configuration file path
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.authenticator = self._initialize_authenticator()

    def _load_config(self):
        """Load YAML configuration file"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                config = yaml.load(file, Loader=SafeLoader)
            return config
        except FileNotFoundError:
            st.error(f"Configuration file not found: {self.config_path}")
            st.stop()
        except Exception as e:
            st.error(f"Error loading configuration file: {str(e)}")
            st.stop()

    def _initialize_authenticator(self):
        """Initialize Streamlit Authenticator"""
        try:
            # Hash passwords (only on first run)
            if self._need_password_hashing():
                stauth.Hasher.hash_passwords(self.config["credentials"])
                self._save_config()

            authenticator = stauth.Authenticate(
                self.config["credentials"],
                self.config["cookie"]["name"],
                self.config["cookie"]["key"],
                self.config["cookie"]["expiry_days"],
            )
            return authenticator
        except Exception as e:
            st.error(f"Error initializing authentication system: {str(e)}")
            st.stop()

    def _need_password_hashing(self):
        """Check if password hashing is needed"""
        for username, user_data in self.config["credentials"]["usernames"].items():
            password = user_data.get("password", "")
            # If there's a plain text password that's not a bcrypt hash, hashing is needed
            if not password.startswith("$2b$"):
                return True
        return False

    def _save_config(self):
        """Save configuration file"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as file:
                yaml.dump(
                    self.config, file, default_flow_style=False, allow_unicode=True
                )
        except Exception as e:
            st.warning(f"Error saving configuration file: {str(e)}")

    def render_login(self):
        """
        Render login widget

        Returns:
            bool: Login success status
        """
        try:
            # Render login widget
            self.authenticator.login()

            # Check login status
            if st.session_state.get("authentication_status"):
                return True
            elif st.session_state.get("authentication_status") is False:
                st.error("❌ Incorrect username/password")
                return False
            elif st.session_state.get("authentication_status") is None:
                st.warning("🔐 Please enter your username and password")
                return False

        except Exception as e:
            st.error(f"Error during login process: {str(e)}")
            return False

    def render_logout(self, location="sidebar"):
        """
        Render logout button

        Args:
            location (str): Logout button location ('main', 'sidebar')
        """
        try:
            self.authenticator.logout(location=location)
        except Exception as e:
            st.error(f"Error during logout process: {str(e)}")

    def get_user_info(self):
        """
        Return current logged-in user information

        Returns:
            dict: User information (name, username, roles, etc.)
        """
        if not st.session_state.get("authentication_status"):
            return None

        username = st.session_state.get("username")
        if not username:
            return None

        user_data = self.config["credentials"]["usernames"].get(username, {})

        return {
            "name": st.session_state.get("name"),
            "username": username,
            "email": user_data.get("email"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "roles": user_data.get("roles", []),
        }

    def is_logged_in(self):
        """Check login status"""
        return st.session_state.get("authentication_status", False)

    def render_user_info(self, location="sidebar"):
        """
        Display user information

        Args:
            location (str): Display location ('main', 'sidebar')
        """
        user_info = self.get_user_info()
        if not user_info:
            return
        
        # Only show logout button, no user info text
        self.render_logout(location)


def initialize_auth():
    """Initialize authentication manager (session state management)"""
    if "auth_manager" not in st.session_state:
        st.session_state.auth_manager = AuthenticationManager()
    return st.session_state.auth_manager

