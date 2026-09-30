from datetime import datetime
from models import db

COMMON_GOAL_PRESETS = [
    'Emergency Fund',
    'Laptop / Workstation',
    'Higher Education',
    'Travel & Vacation',
    'Home Renovation',
    'Vehicle Down Payment',
    'Personal Goal'
]


class SavingsGoal(db.Model):
    __tablename__ = 'savings_goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0, nullable=False)
    target_date = db.Column(db.String(10), nullable=False)  # Format: YYYY-MM-DD
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        target = float(self.target_amount)
        current = float(self.current_amount)
        progress_pct = round((current / target * 100), 1) if target > 0 else 0.0
        remaining = max(0.0, target - current)

        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'target_amount': round(target, 2),
            'current_amount': round(current, 2),
            'target_date': self.target_date,
            'progress_percentage': min(100.0, progress_pct),
            'remaining_amount': round(remaining, 2),
            'is_completed': current >= target,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self) -> str:
        return f'<SavingsGoal {self.name}: ₹{self.current_amount}/₹{self.target_amount}>'
