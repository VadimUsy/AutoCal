from app.models.event import Event

class EventValidator:
    """Validator for event data"""
    
    @staticmethod
    def validate(event: Event) -> tuple[bool, str]:
        """
        Validate event data
        Returns: (is_valid, error_message)
        """
        if not event.title or not event.title.strip():
            return False, "Event title is required"
        
        if not (1000 <= event.year <= 9999):
            return False, "Year must be between 1000 and 9999"
        
        if not (1 <= event.month <= 12):
            return False, "Month must be between 1 and 12"
        
        if not (1 <= event.day <= 31):
            return False, "Day must be between 1 and 31"
        
        if not (1 <= event.hour <= 12):
            return False, "Hour must be between 1 and 12"
        
        if not (0 <= event.minute <= 59):
            return False, "Minute must be between 0 and 59"
        
        if event.ampm not in ['AM', 'PM']:
            return False, "AM/PM must be either 'AM' or 'PM'"
        
        return True, ""