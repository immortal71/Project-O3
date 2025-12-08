"""
Input validation and sanitization for OncoPurpose API
Implements comprehensive validation for security and data integrity
"""

# Copyright (c) 2025 OncoPurpose (trovesx)
# All Rights Reserved.
# For licensing info, see LICENSE or contact oncopurpose@trovesx.com

import re
import html
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import structlog
from pydantic import BaseModel, validator, constr

logger = structlog.get_logger()


class ValidationConfig:
    """Configuration for validation rules"""
    MAX_STRING_LENGTH = 1000
    MAX_TEXT_LENGTH = 10000
    ALLOWED_FILE_EXTENSIONS = {'.pdf', '.txt', '.csv', '.json', '.xml'}
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'text/plain',
        'text/csv',
        'application/json',
        'application/xml',
        'text/xml'
    }
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class InputSanitizer:
    """Sanitization utilities for user inputs"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = ValidationConfig.MAX_STRING_LENGTH) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            return str(value)
        
        # Remove leading/trailing whitespace
        value = value.strip()
        
        # Limit length
        if len(value) > max_length:
            value = value[:max_length]
            logger.warning("String truncated due to length limit", original_length=len(value))
        
        # Escape HTML to prevent XSS
        value = html.escape(value, quote=True)
        
        # Remove null bytes and control characters
        value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
        
        return value
    
    @staticmethod
    def sanitize_text(value: str, max_length: int = ValidationConfig.MAX_TEXT_LENGTH) -> str:
        """Sanitize longer text input"""
        return InputSanitizer.sanitize_string(value, max_length)
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """Validate and sanitize email address"""
        if not isinstance(email, str):
            raise ValueError("Email must be a string")
        
        email = email.strip().lower()
        
        # Basic email regex pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        
        return email
    
    @staticmethod
    def sanitize_url(url: str, allowed_schemes: List[str] = None) -> str:
        """Validate and sanitize URL"""
        if not isinstance(url, str):
            raise ValueError("URL must be a string")
        
        url = url.strip()
        
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if allowed_schemes and parsed.scheme not in allowed_schemes:
                raise ValueError(f"URL scheme not allowed. Allowed: {allowed_schemes}")
            
            # Check for dangerous characters
            if any(char in url for char in ['<', '>', '"', "'", '(', ')', '{', '}', '|', '\\', '^']):
                raise ValueError("URL contains dangerous characters")
            
            return url
            
        except Exception as e:
            raise ValueError(f"Invalid URL format: {str(e)}")
    
    @staticmethod
    def sanitize_smiles(smiles: str) -> str:
        """Sanitize SMILES notation for chemical compounds"""
        if not isinstance(smiles, str):
            raise ValueError("SMILES must be a string")
        
        smiles = smiles.strip()
        
        # Basic SMILES validation
        # Remove any whitespace
        smiles = re.sub(r'\s+', '', smiles)
        
        # Check for common SMILES patterns
        if not re.match(r'^[A-Za-z0-9@+\-\[\]\\/=\\#\\$\\(\\)\\.\\*]+$', smiles):
            raise ValueError("Invalid SMILES notation")
        
        return smiles
    
    @staticmethod
    def sanitize_search_query(query: str) -> str:
        """Sanitize search queries"""
        if not isinstance(query, str):
            return ""
        
        query = query.strip()
        
        # Remove SQL injection patterns
        sql_patterns = [
            r'(\bOR\b|\bAND\b)\s*\d+\s*=\s*\d+',  # SQL injection patterns
            r'\bUNION\b.*\bSELECT\b',
            r'\bINSERT\b.*\bINTO\b',
            r'\bDELETE\b.*\bFROM\b',
            r'\bDROP\b.*\bTABLE\b',
            r'\bUPDATE\b.*\bSET\b',
            r'--',  # SQL comment
            r'/\*',  # SQL comment start
            r'\*/',  # SQL comment end
        ]
        
        for pattern in sql_patterns:
            query = re.sub(pattern, '', query, flags=re.IGNORECASE)
        
        # Remove special characters except basic search operators
        query = re.sub(r'[^\w\s\-\+"\'\*]', ' ', query)
        
        # Remove multiple spaces
        query = re.sub(r'\s+', ' ', query).strip()
        
        return query
    
    @staticmethod
    def validate_file_upload(filename: str, content_type: str, size: int) -> None:
        """Validate file upload parameters"""
        if not filename:
            raise ValueError("Filename is required")
        
        # Check file extension
        import os
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ValidationConfig.ALLOWED_FILE_EXTENSIONS:
            raise ValueError(f"File extension not allowed. Allowed: {ValidationConfig.ALLOWED_FILE_EXTENSIONS}")
        
        # Check MIME type
        if content_type not in ValidationConfig.ALLOWED_MIME_TYPES:
            raise ValueError(f"Content type not allowed. Allowed: {ValidationConfig.ALLOWED_MIME_TYPES}")
        
        # Check file size
        if size > ValidationConfig.MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds limit. Max: {ValidationConfig.MAX_FILE_SIZE} bytes")


class SecurityValidator(BaseModel):
    """Base class for security validation"""
    
    @validator('*', pre=True)
    def validate_all_fields(cls, v):
        """Apply security validation to all fields"""
        if isinstance(v, str):
            # Check for potential XSS patterns
            xss_patterns = [
                r'<script[^>]*>.*?</script>',
                r'javascript:',
                r'vbscript:',
                r'on\w+\s*=',
                r'<iframe[^>]*>',
                r'<object[^>]*>',
                r'<embed[^>]*>',
                r'<link[^>]*>',
                r'<meta[^>]*>',
                r'<style[^>]*>',
            ]
            
            for pattern in xss_patterns:
                if re.search(pattern, v, re.IGNORECASE):
                    raise ValueError("Potential XSS detected in input")
        
        return v


class SafeString(constr):
    """Safe string type with validation"""
    strip_whitespace = True
    min_length = 1
    max_length = ValidationConfig.MAX_STRING_LENGTH
    regex = r'^[^<>&"\'\\]+$'  # Basic HTML/XSS prevention


class SafeText(constr):
    """Safe text type for longer content"""
    strip_whitespace = True
    min_length = 1
    max_length = ValidationConfig.MAX_TEXT_LENGTH


# Validation schemas for common inputs
class SearchQuerySchema(BaseModel):
    query: SafeString
    limit: Optional[int] = 10
    offset: Optional[int] = 0
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Limit must be between 1 and 100')
        return v
    
    @validator('offset')
    def validate_offset(cls, v):
        if v < 0:
            raise ValueError('Offset must be non-negative')
        return v


class FileUploadSchema(BaseModel):
    filename: SafeString
    content_type: SafeString
    size: int
    
    @validator('size')
    def validate_size(cls, v):
        if v <= 0:
            raise ValueError('File size must be positive')
        if v > ValidationConfig.MAX_FILE_SIZE:
            raise ValueError(f'File size exceeds maximum of {ValidationConfig.MAX_FILE_SIZE} bytes')
        return v
    
    @validator('content_type')
    def validate_content_type(cls, v):
        if v not in ValidationConfig.ALLOWED_MIME_TYPES:
            raise ValueError(f'Content type not allowed')
        return v


class ValidationMiddleware:
    """Middleware for input validation"""
    
    def __init__(self):
        self.sanitizer = InputSanitizer()
    
    async def validate_request(self, request) -> Dict[str, Any]:
        """Validate incoming request data"""
        validation_errors = {}
        
        # Validate query parameters
        if request.query_params:
            for key, value in request.query_params.items():
                try:
                    # Sanitize query parameter values
                    sanitized = self.sanitizer.sanitize_string(value)
                    if sanitized != value:
                        logger.warning("Query parameter sanitized", key=key, original=value, sanitized=sanitized)
                except Exception as e:
                    validation_errors[f'query.{key}'] = str(e)
        
        # Validate headers
        for key, value in request.headers.items():
            if key.lower() in ['authorization', 'content-type', 'accept']:
                continue  # Skip standard headers
            
            try:
                sanitized = self.sanitizer.sanitize_string(value)
                if sanitized != value:
                    logger.warning("Header sanitized", key=key, original=value, sanitized=sanitized)
            except Exception as e:
                validation_errors[f'header.{key}'] = str(e)
        
        if validation_errors:
            raise ValueError(f"Validation errors: {validation_errors}")
        
        return validation_errors
    
    def validate_smiles(self, smiles: str) -> str:
        """Validate and sanitize SMILES notation"""
        try:
            return self.sanitizer.sanitize_smiles(smiles)
        except Exception as e:
            raise ValueError(f"Invalid SMILES notation: {str(e)}")
    
    def validate_search_query(self, query: str) -> str:
        """Validate and sanitize search query"""
        try:
            return self.sanitizer.sanitize_search_query(query)
        except Exception as e:
            raise ValueError(f"Invalid search query: {str(e)}")


# Global validation instance
validation_middleware = ValidationMiddleware()