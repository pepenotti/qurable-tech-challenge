"""
Code generation service for creating unique coupon codes
"""
import string
import secrets
from typing import List, Optional
from app.config import get_settings


class CodeGenerator:
    """Generates unique coupon codes based on patterns"""
    
    def __init__(self):
        self.settings = get_settings()
        self.charset = self.settings.CODE_GENERATION_CHARSET
    
    def generate_codes(
        self, 
        count: int, 
        pattern: Optional[str] = None, 
        length: int = 8,
        existing_codes: set = None
    ) -> List[str]:
        """
        Generate unique coupon codes
        
        Args:
            count: Number of codes to generate
            pattern: Optional pattern with {} placeholder (e.g., 'SUMMER2024-{}')
            length: Length of random part
            existing_codes: Set of existing codes to avoid collisions
            
        Returns:
            List of unique generated codes
        """
        if existing_codes is None:
            existing_codes = set()
        
        codes = []
        max_attempts = count * 10  # Prevent infinite loops
        attempts = 0
        
        while len(codes) < count and attempts < max_attempts:
            code = self._generate_single_code(pattern, length)
            
            # Ensure uniqueness within batch and against existing codes
            if code not in codes and code not in existing_codes:
                codes.append(code)
            
            attempts += 1
        
        if len(codes) < count:
            raise ValueError(f"Could not generate {count} unique codes. Only generated {len(codes)}. "
                           f"Consider increasing code length or changing pattern.")
        
        return codes
    
    def _generate_single_code(self, pattern: Optional[str], length: int) -> str:
        """Generate a single random code"""
        random_part = ''.join(secrets.choice(self.charset) for _ in range(length))
        
        if pattern:
            # Replace {} placeholder with random part
            if '{}' in pattern:
                return pattern.format(random_part)
            else:
                # If no placeholder, append random part
                return f"{pattern}{random_part}"
        
        return random_part
    
    @staticmethod
    def validate_pattern(pattern: str) -> bool:
        """Validate that pattern is acceptable"""
        if not pattern:
            return True
        
        # Check length
        if len(pattern) > 40:  # Leave room for random part
            return False
        
        # Pattern should contain only alphanumeric, dash, underscore, and {}
        allowed = set(string.ascii_letters + string.digits + '-_{}')
        if not set(pattern).issubset(allowed):
            return False
        
        return True
