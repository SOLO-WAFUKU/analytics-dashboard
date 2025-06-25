"""Configuration manager for handling credentials securely.

This module provides functions to manage API credentials through
Streamlit's session state and secrets management.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional

import streamlit as st
from cryptography.fernet import Fernet
from loguru import logger


def get_encryption_key() -> bytes:
    """Get or create encryption key for storing credentials.
    
    Returns:
        bytes: Encryption key
    """
    key_path = Path(".streamlit/secrets.toml")
    key_path.parent.mkdir(exist_ok=True)
    
    if key_path.exists():
        with open(key_path, "r") as f:
            content = f.read()
            if "encryption_key" in content:
                # Extract key from toml format
                for line in content.split("\n"):
                    if line.startswith("encryption_key"):
                        key = line.split("=")[1].strip().strip('"')
                        return key.encode()
    
    # Generate new key
    key = Fernet.generate_key()
    with open(key_path, "a") as f:
        f.write(f'\nencryption_key = "{key.decode()}"\n')
    
    return key


def save_credentials(credentials: Dict[str, str]) -> bool:
    """Save credentials to encrypted file.
    
    Args:
        credentials: Dictionary of credentials
    
    Returns:
        bool: True if successful
    """
    try:
        # Create .streamlit directory if not exists
        os.makedirs(".streamlit", exist_ok=True)
        
        # Encrypt credentials
        key = get_encryption_key()
        fernet = Fernet(key)
        
        # Convert to JSON and encrypt
        json_creds = json.dumps(credentials)
        encrypted = fernet.encrypt(json_creds.encode())
        
        # Save to file
        creds_path = Path(".streamlit/credentials.enc")
        with open(creds_path, "wb") as f:
            f.write(encrypted)
        
        # Also update .env file for local development
        update_env_file(credentials)
        
        logger.info("Credentials saved successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error saving credentials: {str(e)}")
        return False


def load_credentials() -> Optional[Dict[str, str]]:
    """Load credentials from encrypted file.
    
    Returns:
        Optional[Dict[str, str]]: Credentials dictionary or None
    """
    try:
        creds_path = Path(".streamlit/credentials.enc")
        if not creds_path.exists():
            # Try loading from .env as fallback
            return load_from_env()
        
        # Load and decrypt
        key = get_encryption_key()
        fernet = Fernet(key)
        
        with open(creds_path, "rb") as f:
            encrypted = f.read()
        
        decrypted = fernet.decrypt(encrypted)
        credentials = json.loads(decrypted.decode())
        
        return credentials
        
    except Exception as e:
        logger.error(f"Error loading credentials: {str(e)}")
        return load_from_env()


def load_from_env() -> Optional[Dict[str, str]]:
    """Load credentials from .env file.
    
    Returns:
        Optional[Dict[str, str]]: Credentials dictionary or None
    """
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        credentials = {}
        for key in ["GA_PROPERTY_ID", "STRIPE_API_KEY", "OPENAI_API_KEY", "TW_BEARER_TOKEN"]:
            value = os.getenv(key)
            if value and value != f"your_{key.lower()}_here":
                credentials[key] = value
        
        return credentials if credentials else None
        
    except Exception as e:
        logger.error(f"Error loading from .env: {str(e)}")
        return None


def update_env_file(credentials: Dict[str, str]) -> None:
    """Update .env file with new credentials.
    
    Args:
        credentials: Dictionary of credentials
    """
    try:
        env_path = Path(".env")
        
        # Read existing content
        if env_path.exists():
            with open(env_path, "r") as f:
                lines = f.readlines()
        else:
            lines = []
        
        # Update or add credentials
        updated_lines = []
        updated_keys = set()
        
        for line in lines:
            if "=" in line:
                key = line.split("=")[0].strip()
                if key in credentials:
                    updated_lines.append(f"{key}={credentials[key]}\n")
                    updated_keys.add(key)
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
        
        # Add missing keys
        for key, value in credentials.items():
            if key not in updated_keys and value:
                updated_lines.append(f"{key}={value}\n")
        
        # Write back
        with open(env_path, "w") as f:
            f.writelines(updated_lines)
            
    except Exception as e:
        logger.error(f"Error updating .env file: {str(e)}")


def validate_credentials(credentials: Dict[str, str]) -> Dict[str, bool]:
    """Validate credential format.
    
    Args:
        credentials: Dictionary of credentials
    
    Returns:
        Dict[str, bool]: Validation results
    """
    validations = {}
    
    # GA Property ID - should be numeric
    ga_id = credentials.get("GA_PROPERTY_ID", "")
    validations["GA_PROPERTY_ID"] = ga_id.isdigit() and len(ga_id) > 0
    
    # Stripe API Key - should start with sk_live_ or sk_test_
    stripe_key = credentials.get("STRIPE_API_KEY", "")
    validations["STRIPE_API_KEY"] = (
        stripe_key.startswith("sk_live_") or stripe_key.startswith("sk_test_")
    ) and len(stripe_key) > 10
    
    # OpenAI API Key - should start with sk-
    openai_key = credentials.get("OPENAI_API_KEY", "")
    validations["OPENAI_API_KEY"] = (
        openai_key.startswith("sk-") and len(openai_key) > 10
    )
    
    # Twitter Bearer Token - optional, but if provided should be long
    tw_token = credentials.get("TW_BEARER_TOKEN", "")
    validations["TW_BEARER_TOKEN"] = (
        len(tw_token) == 0 or len(tw_token) > 20
    )
    
    return validations


def get_credential_status() -> Dict[str, str]:
    """Get status of each credential.
    
    Returns:
        Dict[str, str]: Status for each credential
    """
    credentials = load_credentials() or {}
    validations = validate_credentials(credentials)
    
    status = {}
    for key in ["GA_PROPERTY_ID", "STRIPE_API_KEY", "OPENAI_API_KEY", "TW_BEARER_TOKEN"]:
        if key not in credentials or not credentials[key]:
            status[key] = "❌ Not configured"
        elif not validations.get(key, False):
            status[key] = "⚠️ Invalid format"
        else:
            # Mask the credential for display
            value = credentials[key]
            if len(value) > 10:
                masked = value[:6] + "..." + value[-4:]
            else:
                masked = value[:3] + "..."
            status[key] = f"✅ Configured ({masked})"
    
    return status