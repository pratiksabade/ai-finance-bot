from datetime import datetime
from flask import Blueprint, request, jsonify, session
from routes.auth import login_required
from services.finance_service import FinanceService

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


@dashboard_bp.route('', methods=['GET'])
@login_required
def get_dashboard_data():
    """Returns calculated financial aggregates and status for the user."""
    user_id = session.get('user_id')
    month = request.args.get('month')
    if not month:
        month = datetime.utcnow().strftime('%Y-%m')

    summary = FinanceService.get_user_dashboard_summary(user_id, target_month=month)

    # If the user has completely empty records, supply realistic demo baseline values
    if not summary.get('has_data'):
        demo_category_spending = {
            'Rent': 18000.0,
            'Food': 11200.0,
            'Shopping': 6000.0,
            'Transport': 4500.0,
            'Utilities': 3500.0,
            'Entertainment': 3000.0,
            'Healthcare': 2000.0
        }
        demo_budget_comparison = [
            {'category': 'Rent', 'limit': 18000.0, 'spent': 18000.0, 'remaining': 0.0, 'percentage': 100.0, 'status': 'warning'},
            {'category': 'Food', 'limit': 12000.0, 'spent': 11200.0, 'remaining': 800.0, 'percentage': 93.3, 'status': 'warning'},
            {'category': 'Shopping', 'limit': 5000.0, 'spent': 6000.0, 'remaining': -1000.0, 'percentage': 120.0, 'status': 'exceeded'},
            {'category': 'Transport', 'limit': 5000.0, 'spent': 4500.0, 'remaining': 500.0, 'percentage': 90.0, 'status': 'warning'},
            {'category': 'Utilities', 'limit': 4000.0, 'spent': 3500.0, 'remaining': 500.0, 'percentage': 87.5, 'status': 'warning'},
            {'category': 'Healthcare', 'limit': 3000.0, 'spent': 2000.0, 'remaining': 1000.0, 'percentage': 66.7, 'status': 'safe'}
        ]
        demo_goals = [
            {
                'id': 101,
                'name': 'Emergency Reserve Fund (6 Months)',
                'target_amount': 250000.0,
                'current_amount': 145000.0,
                'target_date': '2026-12-31',
                'progress_percentage': 58.0,
                'remaining_amount': 105000.0,
                'is_completed': False
            },
            {
                'id': 102,
                'name': 'Workstation Laptop Setup',
                'target_amount': 95000.0,
                'current_amount': 62000.0,
                'target_date': '2026-11-15',
                'progress_percentage': 65.3,
                'remaining_amount': 33000.0,
                'is_completed': False
            }
        ]

        summary.update({
            'is_demo_baseline': True,
            'total_income': 85000.0,
            'total_income_formatted': '₹85,000.00',
            'total_expense': 48200.0,
            'total_expense_formatted': '₹48,200.00',
            'savings': 36800.0,
            'savings_formatted': '₹36,800.00',
            'savings_percentage': 43.3,
            'total_budget_limit': 47000.0,
            'total_budget_limit_formatted': '₹47,000.00',
            'remaining_budget': -1200.0,
            'remaining_budget_formatted': '-₹1,200.00',
            'category_spending': demo_category_spending,
            'budget_comparison': demo_budget_comparison,
            'goals': demo_goals,
            'goals_summary': {
                'total_goals': 2,
                'total_target': 345000.0,
                'total_target_formatted': '₹3,45,000.00',
                'total_saved': 207000.0,
                'total_saved_formatted': '₹2,07,000.00',
                'progress_percentage': 60.0
            },
            'recent_transactions': [
                {'id': 1, 'type': 'income', 'title': 'Tech Corp Salary', 'category': 'Income', 'amount': 75000.0, 'date': f"{month}-01", 'description': 'Monthly primary payroll'},
                {'id': 2, 'type': 'income', 'title': 'Consulting Retainer', 'category': 'Income', 'amount': 10000.0, 'date': f"{month}-05", 'description': 'Architecture advisory retainer'},
                {'id': 3, 'type': 'expense', 'title': 'Apartment Lease', 'category': 'Rent', 'amount': 18000.0, 'date': f"{month}-02", 'description': 'Monthly house rent transfer'},
                {'id': 4, 'type': 'expense', 'title': 'Grocery & Provisions', 'category': 'Food', 'amount': 6500.0, 'date': f"{month}-06", 'description': 'Supermarket inventory'},
                {'id': 5, 'type': 'expense', 'title': 'Metro & Fuel Card', 'category': 'Transport', 'amount': 4500.0, 'date': f"{month}-09", 'description': 'Transit reload'},
                {'id': 6, 'type': 'expense', 'title': 'Fiber Internet & Power', 'category': 'Utilities', 'amount': 3500.0, 'date': f"{month}-11", 'description': 'Broadband & electricity'},
                {'id': 7, 'type': 'expense', 'title': 'Ergonomic Desk Chair', 'category': 'Shopping', 'amount': 6000.0, 'date': f"{month}-14", 'description': 'Workplace chair procurement'},
                {'id': 8, 'type': 'expense', 'title': 'Dining & Cafes', 'category': 'Food', 'amount': 4700.0, 'date': f"{month}-18", 'description': 'Weekend dinner'},
                {'id': 9, 'type': 'expense', 'title': 'Annual Medical Checkup', 'category': 'Healthcare', 'amount': 2000.0, 'date': f"{month}-22", 'description': 'Diagnostic health lab'},
                {'id': 10, 'type': 'expense', 'title': 'Books & Digital Media', 'category': 'Entertainment', 'amount': 3000.0, 'date': f"{month}-25", 'description': 'Technical publications'}
            ]
        })

    return jsonify({
        'status': 'success',
        'data': summary
    })
