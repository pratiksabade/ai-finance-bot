from datetime import datetime
from collections import defaultdict
from sqlalchemy import func
from models import db, Income, Expense, Budget, SavingsGoal


class FinanceService:
    """Core financial analytics and calculation engine."""

    @staticmethod
    def format_inr(amount: float) -> str:
        """Format an amount into Indian Rupee format (e.g., ₹1,50,000.00)."""
        try:
            val = float(amount)
            is_negative = val < 0
            val = abs(val)
            cents = f"{val:.2f}".split('.')[1]
            whole = int(val)
            s = str(whole)
            if len(s) <= 3:
                formatted_whole = s
            else:
                last_three = s[-3:]
                remaining = s[:-3]
                groups = []
                while len(remaining) > 2:
                    groups.insert(0, remaining[-2:])
                    remaining = remaining[:-2]
                if remaining:
                    groups.insert(0, remaining)
                groups.append(last_three)
                formatted_whole = ','.join(groups)
            prefix = "-₹" if is_negative else "₹"
            return f"{prefix}{formatted_whole}.{cents}"
        except (ValueError, TypeError):
            return "₹0.00"

    @classmethod
    def get_user_dashboard_summary(cls, user_id: int, target_month: str = None) -> dict:
        """
        Calculates all financial aggregates for the user.
        If target_month is omitted, defaults to the current UTC month (YYYY-MM).
        """
        now = datetime.utcnow()
        if not target_month:
            target_month = now.strftime('%Y-%m')

        # Check if user has ANY transactions at all
        user_incomes_query = Income.query.filter_by(user_id=user_id)
        user_expenses_query = Expense.query.filter_by(user_id=user_id)
        has_any_data = (user_incomes_query.first() is not None) or (user_expenses_query.first() is not None)

        # Incomes for the target month
        month_incomes = user_incomes_query.filter(Income.date.like(f"{target_month}%")).all()
        # Expenses for the target month
        month_expenses = user_expenses_query.filter(Expense.date.like(f"{target_month}%")).all()

        total_income = round(sum(inc.amount for inc in month_incomes), 2)
        total_expense = round(sum(exp.amount for exp in month_expenses), 2)
        savings = round(total_income - total_expense, 2)

        # Safe savings percentage
        if total_income > 0:
            savings_pct = round((savings / total_income) * 100, 1)
        else:
            savings_pct = 0.0

        # Expenses grouped by category
        category_spending = defaultdict(float)
        for exp in month_expenses:
            category_spending[exp.category] += exp.amount
        category_spending = {k: round(v, 2) for k, v in category_spending.items()}

        # Category budgets comparison
        user_budgets = Budget.query.filter_by(user_id=user_id, month=target_month).all()
        budget_comparison = []
        total_budget_limit = 0.0

        for b in user_budgets:
            cat = b.category
            limit_val = float(b.limit)
            total_budget_limit += limit_val
            spent = category_spending.get(cat, 0.0)
            remaining = round(limit_val - spent, 2)
            pct = round((spent / limit_val * 100), 1) if limit_val > 0 else 0.0
            
            if spent > limit_val:
                status = 'exceeded'
            elif pct >= 80.0:
                status = 'warning'
            else:
                status = 'safe'

            budget_comparison.append({
                'id': b.id,
                'category': cat,
                'limit': limit_val,
                'spent': spent,
                'remaining': remaining,
                'percentage': pct,
                'status': status
            })

        remaining_total_budget = round(total_budget_limit - total_expense, 2) if total_budget_limit > 0 else 0.0

        # Recent transactions (combined income + expense)
        all_incomes = user_incomes_query.order_by(Income.date.desc(), Income.id.desc()).limit(10).all()
        all_expenses = user_expenses_query.order_by(Expense.date.desc(), Expense.id.desc()).limit(10).all()

        recent_txs = []
        for inc in all_incomes:
            recent_txs.append({
                'id': inc.id,
                'type': 'income',
                'title': inc.source,
                'category': 'Income',
                'amount': inc.amount,
                'date': inc.date,
                'description': inc.description or ''
            })
        for exp in all_expenses:
            recent_txs.append({
                'id': exp.id,
                'type': 'expense',
                'title': exp.description or exp.category,
                'category': exp.category,
                'amount': exp.amount,
                'date': exp.date,
                'description': exp.description or ''
            })

        # Sort recent transactions by date descending
        recent_txs.sort(key=lambda x: (x['date'], x['id']), reverse=True)
        recent_txs = recent_txs[:10]

        # Monthly Trends (Past 6 months)
        trends = cls.get_monthly_trends(user_id, count=6)

        # Active savings goals
        goals = SavingsGoal.query.filter_by(user_id=user_id).order_by(SavingsGoal.target_date.asc()).all()
        goals_data = [g.to_dict() for g in goals]
        total_target_savings = sum(g['target_amount'] for g in goals_data)
        total_current_savings = sum(g['current_amount'] for g in goals_data)
        goals_progress_pct = round((total_current_savings / total_target_savings * 100), 1) if total_target_savings > 0 else 0.0

        # If user has zero data at all, provide a structured realistic baseline flag
        is_demo_baseline = not has_any_data

        return {
            'target_month': target_month,
            'has_data': has_any_data,
            'is_demo_baseline': is_demo_baseline,
            'currency': 'INR',
            'currency_symbol': '₹',
            'total_income': total_income,
            'total_income_formatted': cls.format_inr(total_income),
            'total_expense': total_expense,
            'total_expense_formatted': cls.format_inr(total_expense),
            'savings': savings,
            'savings_formatted': cls.format_inr(savings),
            'savings_percentage': savings_pct,
            'total_budget_limit': round(total_budget_limit, 2),
            'total_budget_limit_formatted': cls.format_inr(total_budget_limit),
            'remaining_budget': remaining_total_budget,
            'remaining_budget_formatted': cls.format_inr(remaining_total_budget),
            'category_spending': category_spending,
            'budget_comparison': budget_comparison,
            'recent_transactions': recent_txs,
            'trends': trends,
            'goals': goals_data,
            'goals_summary': {
                'total_goals': len(goals_data),
                'total_target': round(total_target_savings, 2),
                'total_target_formatted': cls.format_inr(total_target_savings),
                'total_saved': round(total_current_savings, 2),
                'total_saved_formatted': cls.format_inr(total_current_savings),
                'progress_percentage': goals_progress_pct
            }
        }

    @classmethod
    def get_monthly_trends(cls, user_id: int, count: int = 6) -> dict:
        """Calculates past monthly income vs expense trends."""
        now = datetime.utcnow()
        year = now.year
        month = now.month

        months_list = []
        for _ in range(count):
            months_list.append(f"{year:04d}-{month:02d}")
            month -= 1
            if month == 0:
                month = 12
                year -= 1

        months_list.reverse()

        labels = []
        incomes = []
        expenses = []

        for m_str in months_list:
            # month label: e.g. "Sep 2026"
            dt = datetime.strptime(m_str, '%Y-%m')
            labels.append(dt.strftime('%b %Y'))

            inc_sum = db.session.query(func.coalesce(func.sum(Income.amount), 0.0))\
                .filter(Income.user_id == user_id, Income.date.like(f"{m_str}%")).scalar()
            exp_sum = db.session.query(func.coalesce(func.sum(Expense.amount), 0.0))\
                .filter(Expense.user_id == user_id, Expense.date.like(f"{m_str}%")).scalar()

            incomes.append(round(float(inc_sum), 2))
            expenses.append(round(float(exp_sum), 2))

        return {
            'months': months_list,
            'labels': labels,
            'incomes': incomes,
            'expenses': expenses
        }
