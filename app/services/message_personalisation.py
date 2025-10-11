"""
Message Personalisation Service
Handles dynamic content generation based on user attributes and targeting criteria.
"""

import re
from typing import Dict, Any, Optional
from datetime import datetime

class MessagePersonalisationService:
    """Service for personalising message content based on user attributes."""
    
    def __init__(self):
        # Define available placeholders and their descriptions
        self.placeholders = {
            'first_name': 'User\'s first name',
            'last_name': 'User\'s last name',
            'degree_type': 'User\'s degree type (Masters/PhD)',
            'location': 'User\'s study location (online/on-campus)',
            'enrollment_status': 'User\'s enrollment status (full-time/part-time)',
            'stage': 'User\'s candidature stage',
            'support_needs': 'User\'s support needs (personal/academic/both)',
            'current_week': 'Current week of candidature',
            'total_weeks': 'Total weeks in degree program',
            'progress_percentage': 'Progress percentage through degree',
            'upcoming_deadlines': 'List of upcoming deadlines',
            'unit_codes': 'User\'s enrolled unit codes'
        }
    
    def personalise_content(self, content: str, user_data: Dict[str, Any]) -> str:
        """
        Replace placeholders in message content with user-specific data.
        
        Args:
            content: Message content with placeholders like {{first_name}}
            user_data: Dictionary containing user attributes
            
        Returns:
            Personalised content with placeholders replaced
        """
        if not content:
            return content
            
        # Find all placeholders in the content
        placeholder_pattern = r'\{\{(\w+)\}\}'
        placeholders_found = re.findall(placeholder_pattern, content)
        
        personalised_content = content
        
        for placeholder in placeholders_found:
            if placeholder in self.placeholders:
                replacement = self._get_replacement_value(placeholder, user_data)
                personalised_content = personalised_content.replace(
                    f'{{{{{placeholder}}}}}', 
                    str(replacement)
                )
        
        return personalised_content
    
    def _get_replacement_value(self, placeholder: str, user_data: Dict[str, Any]) -> str:
        """Get the replacement value for a specific placeholder."""
        
        # Direct user data mappings
        direct_mappings = {
            'first_name': user_data.get('first_name', 'Student'),
            'last_name': user_data.get('last_name', ''),
            'degree_type': user_data.get('degree_type', 'HDR'),
            'location': user_data.get('location', 'your location'),
            'enrollment_status': user_data.get('enrollment_status', 'your enrollment'),
            'stage': user_data.get('stage', 'your current stage'),
            'support_needs': user_data.get('support_needs', 'your needs'),
            'unit_codes': user_data.get('unit_codes', 'your units')
        }
        
        if placeholder in direct_mappings:
            return direct_mappings[placeholder]
        
        # Calculated values
        if placeholder == 'current_week':
            return str(user_data.get('current_week', 1))
        
        if placeholder == 'total_weeks':
            degree_type = user_data.get('degree_type', '').lower()
            if degree_type == 'masters':
                return '104'  # ~2 years
            elif degree_type == 'phd':
                return '208'  # ~4 years
            return '104'  # default
        
        if placeholder == 'progress_percentage':
            current_week = user_data.get('current_week', 1)
            total_weeks = int(self._get_replacement_value('total_weeks', user_data))
            percentage = min(100, max(0, (current_week / total_weeks) * 100))
            return f"{percentage:.1f}%"
        
        if placeholder == 'upcoming_deadlines':
            deadlines = user_data.get('upcoming_deadlines', [])
            if not deadlines:
                return 'No upcoming deadlines'
            
            deadline_list = []
            for deadline in deadlines[:3]:  # Show max 3 deadlines
                deadline_list.append(f"- {deadline.get('title', 'Deadline')} (Week {deadline.get('week', '?')})")
            
            return '\n'.join(deadline_list) if deadline_list else 'No upcoming deadlines'
        
        # Default fallback
        return f'[{placeholder}]'
    
    def get_available_placeholders(self) -> Dict[str, str]:
        """Get list of available placeholders for admin reference."""
        return self.placeholders.copy()
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """
        Validate message content and identify any issues with placeholders.
        
        Returns:
            Dictionary with validation results
        """
        if not content:
            return {'valid': False, 'errors': ['Content cannot be empty']}
        
        placeholder_pattern = r'\{\{(\w+)\}\}'
        placeholders_found = re.findall(placeholder_pattern, content)
        
        errors = []
        warnings = []
        
        for placeholder in placeholders_found:
            if placeholder not in self.placeholders:
                errors.append(f'Unknown placeholder: {{{{ {placeholder} }}}}')
        
        # Check for common issues
        if '{{first_name}}' not in content and '{{last_name}}' not in content:
            warnings.append('Consider using {{first_name}} for personalisation')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'placeholders_used': placeholders_found
        }
    
    def get_personalisation_preview(self, content: str, sample_user_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a preview of personalised content using sample data.
        
        Args:
            content: Message content with placeholders
            sample_user_data: Optional sample user data, uses defaults if not provided
            
        Returns:
            Preview of personalised content
        """
        if sample_user_data is None:
            sample_user_data = {
                'first_name': 'Alex',
                'last_name': 'Smith',
                'degree_type': 'PhD',
                'location': 'on-campus',
                'enrollment_status': 'full-time',
                'stage': 'mid-candidature',
                'support_needs': 'both',
                'current_week': 52,
                'upcoming_deadlines': [
                    {'title': 'Confirmation of Candidature', 'week': 56},
                    {'title': 'Annual Progress Report', 'week': 60}
                ],
                'unit_codes': 'CITS3200, CITS3001'
            }
        
        return self.personalise_content(content, sample_user_data)