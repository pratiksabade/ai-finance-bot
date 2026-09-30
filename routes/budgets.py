from datetime import datetime
from flask import Blueprint, request, jsonify, session
from models import db, Budget, Expense
from routes.auth import login_required

budgets_bp = Blueprint('budgets', __name__, url_prefix='/api/budgets')


@budgets_bp.route('', methods=['GET'])
@login_required
def list_budgets():
    user_id = session.get('user_id')
    month = request.args.get('month')
    if not month:
        month = datetime.utcnow().strftime('%Y-%m')

    budgets = Budget.query.filter_by(user_id=user_id, month=month).all()

    # Calculate actual spending per category for this month
    expenses = Expense.query.filter(
        Expense.user_id == user_id,
        Expense.date.like(f"{month}%")
    ).all()

    cat_spent = {}
    for exp in expenses:
        cat_spent[exp.category] = cat_spent.get(exp.category, 0.0) + exp.amount

    result = []
    total_budget = 0.0
    total_spent = 0.0

    for b in budgets:
        limit_val = float(b.limit)
        total_budget += limit_val
        spent = round(cat_spent.get(b.category, 0.0), 2)
        total_spent += spent
        remaining = round(limit_val - spent, 2)
        pct = round((spent / limit_val * 100), 1) if limit_val > 0 else 0.0

        if spent > limit_val:
            status = 'exceeded'
        elif pct >= 80.0:
            status = 'warning'
        else:
            status = 'safe'

        item = b.to_dict()
        item.update({
            'spent': spent,
            'remaining': remaining,
            'percentage': pct,
            'status': status
        })
        result.append(item)

    return jsonify({
        'status': 'success',
        'month': month,
        'count': len(result),
        'total_budget': round(total_budget, 2),
        'total_spent': round(total_spent, 2),
        'budgets': result
    })


@budgets_bp.route('', methods=['POST'])
@login_required
def set_budget():
    user_id = session.get('user_id')
    data = request.get_json() or {}

    month = data.get('month', '').strip()
    category = data.get('category', '').strip()

    try:
        limit = float(data.get('limit', 0))
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'Invalid budget limit value.'}), 400

    if not month:
        month = datetime.utcnow().strftime('%Y-%m')
    if not category:
        return jsonify({'status': 'error', 'message': 'Category is required.'}), 400
    if limit <= 0:
        return jsonify({'status': 'error', 'message': 'Budget limit must be greater than zero.'}), 400

    try:
        # Check if already exists for this user, month, category
        existing = Budget.query.filter_by(user_id=user_id, month=month, category=category).first()
        if existing:
            existing.limit = limit
            db.session.commit()
            return jsonify({
                'status': 'success',
                'message': f'Budget limit for {category} updated to ₹{limit:,.2f}.',
                'budget': existing.to_dict()
            })
        else:
            new_budget = Budget(
                user_id=user_id,
                month=month,
                category=category,
                limit=limit
            )
            db.session.add(new_budget)
            db.session.commit()
            return jsonify({
                'status': 'success',
                'message': f'Budget limit for {category} established at ₹{limit:,.2f}.',
                'budget': new_budget.to_dict()
            }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to set budget: {str(e)}'}), 500


@budgets_bp.route('/<int:budget_id>', methods=['PUT'])
@login_required
def update_budget(budget_id: int):
    user_id = session.get('user_id')
    budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()

    if not budget:
        return jsonify({'status': 'error', 'message': 'Budget record not found.'}), 404

    data = request.get_json() or {}

    if 'limit' in data:
        try:
            val = float(data['limit'])
            if val <= 0:
                return jsonify({'status': 'error', 'message': 'Budget limit must be greater than zero.'}), 400
            budget.limit = val
        except (ValueError, TypeError):
            return jsonify({'status': 'error', 'message': 'Invalid limit value.'}), 400

    if 'category' in data:
        cat = data['category'].strip()
        if not cat:
            return jsonify({'status': 'error', 'message': 'Category cannot be empty.'}), 400
        budget.category = cat

    try:
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Budget limit updated successfully.',
            'budget': budget.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to update budget: {str(e)}'}), 500


@budgets_bp.route('/<int:budget_id>', methods=['DELETE'])
@login_required
def delete_budget(budget_id: int):
    user_id = session.get('user_id')
    budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()

    if not budget:
        return jsonify({'status': 'error', 'message': 'Budget record not found.'}), 404

    try:
        db.session.delete(budget)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Budget limit removed successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to delete budget: {str(e)}'}), 500
