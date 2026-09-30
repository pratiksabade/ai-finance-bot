from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.income import income_bp
from routes.expenses import expenses_bp
from routes.budgets import budgets_bp
from routes.goals import goals_bp
from routes.ai import ai_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'income_bp',
    'expenses_bp',
    'budgets_bp',
    'goals_bp',
    'ai_bp'
]
