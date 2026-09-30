from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User
from models.income import Income
from models.expense import Expense
from models.budget import Budget
from models.savings_goal import SavingsGoal

__all__ = ['db', 'User', 'Income', 'Expense', 'Budget', 'SavingsGoal']
