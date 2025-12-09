from dataclasses import dataclass
from typing import Optional

@dataclass
class Event:
    """Event data model"""
    title: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    ampm: str
    description: Optional[str] = ''
    
    def to_dict(self):
        """Convert event to dictionary"""
        return {
            'title': self.title,
            'year': self.year,
            'month': self.month,
            'day': self.day,
            'hour': self.hour,
            'minute': self.minute,
            'ampm': self.ampm,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create event from dictionary"""
        return cls(
            title=data.get('title', ''),
            year=int(data.get('year', 0)),
            month=int(data.get('month', 0)),
            day=int(data.get('day', 0)),
            hour=int(data.get('hour', 0)),
            minute=int(data.get('minute', 0)),
            ampm=data.get('ampm', 'AM'),
            description=data.get('description', '')
        )