"""
Database Seeding Script for Personal Finance Advisor Bot
Populates realistic demo financial data in Indian Rupees (INR) for development and evaluation.
"""

import sys
from datetime import datetime, timedelta

# Ensure UTF-8 output encoding on Windows terminals
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from app import create_app
from models import db, User, Income, Expense, Budget, SavingsGoal

DEMO_USER_EMAIL = "demo@financeadvisor.in"
DEMO_USER_PASSWORD = "Password@123"
DEMO_USER_NAME = "Aditya Sharma"


def seed_database(reset: bool = False):
    app = create_app()

    with app.app_context():
        if reset:
            print("[INFO] Resetting database tables...")
            db.drop_all()
            db.create_all()
            print("[OK] All database tables cleared and recreated.")
        else:
            db.create_all()

        # Check if demo user already exists
        existing_user = User.query.filter_by(email=DEMO_USER_EMAIL).first()
        if existing_user:
            if not reset:
                print(f"[INFO] Demo user '{DEMO_USER_EMAIL}' already exists.")
                print(f"       Log in using Email: {DEMO_USER_EMAIL} | Password: {DEMO_USER_PASSWORD}")
                return
            else:
                db.session.delete(existing_user)
                db.session.commit()

        print(f"[INFO] Creating demo user: {DEMO_USER_EMAIL}")
        user = User(name=DEMO_USER_NAME, email=DEMO_USER_EMAIL)
        user.set_password(DEMO_USER_PASSWORD)
        db.session.add(user)
        db.session.commit()

        # Current date and month
        today = datetime.utcnow()
        current_month = today.strftime('%Y-%m')
        last_month = (today.replace(day=1) - timedelta(days=1)).strftime('%Y-%m')

        # 1. Incomes (in INR)
        incomes_data = [
            # Current month
            {'amount': 85000.0, 'source': 'Primary Salary (Tech Corp)', 'date': f"{current_month}-01", 'description': 'Monthly regular salary credit'},
            {'amount': 22000.0, 'source': 'Freelance Software Consulting', 'date': f"{current_month}-07", 'description': 'Backend API architecture project milestone'},
            {'amount': 3500.0, 'source': 'Investment Dividends', 'date': f"{current_month}-15", 'description': 'Quarterly equity mutual fund payout'},
            # Previous month
            {'amount': 85000.0, 'source': 'Primary Salary (Tech Corp)', 'date': f"{last_month}-01", 'description': 'Monthly salary'},
            {'amount': 18000.0, 'source': 'Freelance Software Consulting', 'date': f"{last_month}-10", 'description': 'Cloud migration retainer'}
        ]

        for inc in incomes_data:
            db.session.add(Income(
                user_id=user.id,
                amount=inc['amount'],
                source=inc['source'],
                date=inc['date'],
                description=inc['description']
            ))

        # 2. Expenses (in INR)
        expenses_data = [
            # Current month
            {'amount': 24000.0, 'category': 'Rent', 'date': f"{current_month}-02", 'description': '2BHK Apartment Monthly Rent'},
            {'amount': 6500.0, 'category': 'Food', 'date': f"{current_month}-03", 'description': 'Supermarket grocery and vegetables'},
            {'amount': 3800.0, 'category': 'Transport', 'date': f"{current_month}-05", 'description': 'Metro transit card recharge and cab fares'},
            {'amount': 4200.0, 'category': 'Utilities', 'date': f"{current_month}-08", 'description': 'Broadband fiber, electricity, and water bill'},
            {'amount': 8900.0, 'category': 'Shopping', 'date': f"{current_month}-10", 'description': 'Ergonomic office chair and keyboard (exceeded limit)'},
            {'amount': 5400.0, 'category': 'Food', 'date': f"{current_month}-12", 'description': 'Weekly dining out and team lunch'},
            {'amount': 2500.0, 'category': 'Healthcare', 'date': f"{current_month}-14", 'description': 'Prescription vitamins and health insurance copay'},
            {'amount': 4000.0, 'category': 'Education', 'date': f"{current_month}-17", 'description': 'Cloud certification exam fee'},
            {'amount': 3200.0, 'category': 'Entertainment', 'date': f"{current_month}-20", 'description': 'Streaming subscriptions and weekend movie'},
            {'amount': 2300.0, 'category': 'Food', 'date': f"{current_month}-23", 'description': 'Gourmet coffee and snacks'},
            # Previous month
            {'amount': 24000.0, 'category': 'Rent', 'date': f"{last_month}-02", 'description': 'Apartment Rent'},
            {'amount': 13500.0, 'category': 'Food', 'date': f"{last_month}-08", 'description': 'Monthly Groceries & dining'},
            {'amount': 4500.0, 'category': 'Transport', 'date': f"{last_month}-12", 'description': 'Fuel and transit'}
        ]

        for exp in expenses_data:
            db.session.add(Expense(
                user_id=user.id,
                amount=exp['amount'],
                category=exp['category'],
                date=exp['date'],
                description=exp['description']
            ))

        # 3. Monthly Budgets
        budgets_data = [
            {'category': 'Rent', 'limit': 24000.0},
            {'category': 'Food', 'limit': 15000.0},
            {'category': 'Shopping', 'limit': 7000.0},   # Exceeded: 8,900 spent
            {'category': 'Transport', 'limit': 5500.0},  # Warning level: 3,800 spent
            {'category': 'Utilities', 'limit': 4500.0},
            {'category': 'Healthcare', 'limit': 3500.0},
            {'category': 'Education', 'limit': 5000.0},
            {'category': 'Entertainment', 'limit': 4000.0}
        ]

        for b in budgets_data:
            db.session.add(Budget(
                user_id=user.id,
                month=current_month,
                category=b['category'],
                limit=b['limit']
            ))

        # 4. Savings Goals
        goals_data = [
            {
                'name': 'Emergency Reserve Fund (6 Months Expenses)',
                'target_amount': 300000.0,
                'current_amount': 185000.0,
                'target_date': '2026-12-31'
            },
            {
                'name': 'Workstation & MacBook M3 Setup',
                'target_amount': 140000.0,
                'current_amount': 95000.0,
                'target_date': '2026-11-30'
            },
            {
                'name': 'Ladakh Motorbike Expedition',
                'target_amount': 60000.0,
                'current_amount': 28000.0,
                'target_date': '2027-06-15'
            }
        ]

        for g in goals_data:
            db.session.add(SavingsGoal(
                user_id=user.id,
                name=g['name'],
                target_amount=g['target_amount'],
                current_amount=g['current_amount'],
                target_date=g['target_date']
            ))

        db.session.commit()
        print("[OK] Database seeded successfully with realistic Indian Rupee demo records!")
        print("\n================ DEMO CREDENTIALS ================")
        print(f" Email:    {DEMO_USER_EMAIL}")
        print(f" Password: {DEMO_USER_PASSWORD}")
        print(f" Name:     {DEMO_USER_NAME}")
        print(" Currency: Indian Rupee (INR / ₹)")
        print("===================================================\n")


if __name__ == '__main__':
    reset_flag = '--reset' in sys.argv
    seed_database(reset=reset_flag)
