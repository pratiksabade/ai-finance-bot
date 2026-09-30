from datetime import datetime
from models import db

EXPENSE_CATEGORIES = [
    'Food',
    'Rent',
    'Transport',
    'Education',
    'Healthcare',
    'Entertainment',
    'Shopping',
    'Utilities',
    'Other'
]


class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    date = db.Column(db.String(10), nullable=False, index=True)  # ISO format: YYYY-MM-DD
    description = db.Column(db.String(255), default='', nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': round(float(self.amount), 2),
            'category': self.category,
            'date': self.date,
            'description': self.description or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self) -> str:
        return f'<Expense ₹{self.amount} for {self.category}>'
