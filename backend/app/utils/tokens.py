# Token Utilities for 3D Print Management System
"""
Secure token generation and validation utilities for email confirmations,
password resets, and other time-sensitive operations.
"""

import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from flask import current_app
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature


class TokenManager:
    """Manager for secure token operations."""
    
    def __init__(self):
        self.serializer = None
    
    def _get_serializer(self):
        """Get URLSafeTimedSerializer instance."""
        if not self.serializer:
            self.serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return self.serializer
    
    def generate_confirmation_token(self, job_id: str, action: str = 'confirm', expires_hours: int = 168) -> str:
        """
        Generate secure confirmation token.
        
        Args:
            job_id: Job ID to encode
            action: Action type ('confirm', 'cancel', etc.)
            expires_hours: Token expiration in hours (default 7 days)
            
        Returns:
            Secure token string
        """
        serializer = self._get_serializer()
        payload = {
            'job_id': job_id,
            'action': action,
            'issued_at': datetime.utcnow().isoformat()
        }
        return serializer.dumps(payload)
    
    def verify_token(self, token: str, expected_action: str = 'confirm', max_age: int = 604800) -> Optional[Dict[str, Any]]:
        """
        Verify token and extract payload.
        
        Args:
            token: Token to verify
            expected_action: Expected action type
            max_age: Maximum age in seconds (default 7 days)
            
        Returns:
            Token payload if valid, None if invalid/expired
        """
        try:
            serializer = self._get_serializer()
            payload = serializer.loads(token, max_age=max_age)
            
            if payload.get('action') == expected_action:
                return payload
        except (SignatureExpired, BadSignature) as e:
            current_app.logger.warning(f"Token verification failed: {str(e)}")
        except Exception as e:
            current_app.logger.error(f"Token verification error: {str(e)}")
        
        return None
    
    def generate_resend_token(self, email: str, job_id: str) -> str:
        """
        Generate token for resending confirmations.
        
        Args:
            email: Student email
            job_id: Job ID
            
        Returns:
            Secure token for resend operations
        """
        serializer = self._get_serializer()
        payload = {
            'email': email,
            'job_id': job_id,
            'action': 'resend',
            'issued_at': datetime.utcnow().isoformat()
        }
        return serializer.dumps(payload)
    
    def verify_resend_token(self, token: str, max_age: int = 3600) -> Optional[Dict[str, Any]]:
        """
        Verify resend token (shorter expiration).
        
        Args:
            token: Token to verify
            max_age: Maximum age in seconds (default 1 hour)
            
        Returns:
            Token payload if valid, None if invalid/expired
        """
        return self.verify_token(token, expected_action='resend', max_age=max_age)
    
    def generate_secure_id(self, length: int = 32) -> str:
        """
        Generate cryptographically secure random string.
        
        Args:
            length: Length of random string
            
        Returns:
            Secure random string
        """
        return secrets.token_urlsafe(length)


# Singleton instance
token_manager = TokenManager()