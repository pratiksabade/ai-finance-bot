from flask import Blueprint, request, jsonify, session
from models import db, Expense
from models.expense import EXPENSE_CATEGORIES
from routes.auth import login_required

expenses_bp = Blueprint('expenses', __name__, url_prefix='/api/expenses')


@expenses_bp.route('/categories', methods=['GET'])
def get_categories():
    return jsonify({
        'status': 'success',
        'categories': EXPENSE_CATEGORIES
    })


@expenses_bp.route('', methods=['GET'])
@login_required
def list_expenses():
    user_id = session.get('user_id')
    month = request.args.get('month')
    category = request.args.get('category')

    query = Expense.query.filter_by(user_id=user_id)
    if month:
        query = query.filter(Expense.date.like(f"{month}%"))
    if category and category != 'All':
        query = query.filter_by(category=category)

    expenses = query.order_by(Expense.date.desc(), Expense.id.desc()).all()
    total = sum(e.amount for e in expenses)

    return jsonify({
        'status': 'success',
        'count': len(expenses),
        'total_amount': round(total, 2),
        'expenses': [e.to_dict() for e in expenses]
    })


@expenses_bp.route('', methods=['POST'])
@login_required
def add_expense():
    user_id = session.get('user_id')
    data = request.get_json() or {}

    try:
        amount = float(data.get('amount', 0))
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'Invalid amount value.'}), 400

    category = data.get('category', '').strip()
    date_str = data.get('date', '').strip()
    description = data.get('description', '').strip()

    if amount <= 0:
        return jsonify({'status': 'error', 'message': 'Amount must be greater than zero.'}), 400
    if not category:
        return jsonify({'status': 'error', 'message': 'Expense category is required.'}), 400
    if not date_str:
        return jsonify({'status': 'error', 'message': 'Date is required.'}), 400

    try:
        new_expense = Expense(
            user_id=user_id,
            amount=amount,
            category=category,
            date=date_str,
            description=description
        )
        db.session.add(new_expense)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Expense record logged successfully.',
            'expense': new_expense.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to add expense: {str(e)}'}), 500


@expenses_bp.route('/<int:expense_id>', methods=['PUT'])
@login_required
def update_expense(expense_id: int):
    user_id = session.get('user_id')
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense:
        return jsonify({'status': 'error', 'message': 'Expense record not found.'}), 404

    data = request.get_json() or {}

    if 'amount' in data:
        try:
            val = float(data['amount'])
            if val <= 0:
                return jsonify({'status': 'error', 'message': 'Amount must be greater than zero.'}), 400
            expense.amount = val
        except (ValueError, TypeError):
            return jsonify({'status': 'error', 'message': 'Invalid amount value.'}), 400

    if 'category' in data:
        cat = data['category'].strip()
        if not cat:
            return jsonify({'status': 'error', 'message': 'Category cannot be empty.'}), 400
        expense.category = cat

    if 'date' in data:
        dt = data['date'].strip()
        if not dt:
            return jsonify({'status': 'error', 'message': 'Date cannot be empty.'}), 400
        expense.date = dt

    if 'description' in data:
        expense.description = data['description'].strip()

    try:
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Expense record updated successfully.',
            'expense': expense.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to update expense: {str(e)}'}), 500


@expenses_bp.route('/<int:expense_id>', methods=['DELETE'])
@login_required
def delete_expense(expense_id: int):
    user_id = session.get('user_id')
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense:
        return jsonify({'status': 'error', 'message': 'Expense record not found.'}), 404

    try:
        db.session.delete(expense)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Expense record deleted successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to delete expense: {str(e)}'}), 500
