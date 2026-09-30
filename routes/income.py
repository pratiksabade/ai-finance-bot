from flask import Blueprint, request, jsonify, session
from models import db, Income
from routes.auth import login_required

income_bp = Blueprint('income', __name__, url_prefix='/api/income')


@income_bp.route('', methods=['GET'])
@login_required
def list_income():
    user_id = session.get('user_id')
    month = request.args.get('month')

    query = Income.query.filter_by(user_id=user_id)
    if month:
        query = query.filter(Income.date.like(f"{month}%"))

    incomes = query.order_by(Income.date.desc(), Income.id.desc()).all()
    total = sum(i.amount for i in incomes)

    return jsonify({
        'status': 'success',
        'count': len(incomes),
        'total_amount': round(total, 2),
        'incomes': [i.to_dict() for i in incomes]
    })


@income_bp.route('', methods=['POST'])
@login_required
def add_income():
    user_id = session.get('user_id')
    data = request.get_json() or {}

    try:
        amount = float(data.get('amount', 0))
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'Invalid amount value.'}), 400

    source = data.get('source', '').strip()
    date_str = data.get('date', '').strip()
    description = data.get('description', '').strip()

    if amount <= 0:
        return jsonify({'status': 'error', 'message': 'Amount must be greater than zero.'}), 400
    if not source:
        return jsonify({'status': 'error', 'message': 'Income source is required.'}), 400
    if not date_str:
        return jsonify({'status': 'error', 'message': 'Date is required.'}), 400

    try:
        new_income = Income(
            user_id=user_id,
            amount=amount,
            source=source,
            date=date_str,
            description=description
        )
        db.session.add(new_income)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Income record added successfully.',
            'income': new_income.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to add income: {str(e)}'}), 500


@income_bp.route('/<int:income_id>', methods=['PUT'])
@login_required
def update_income(income_id: int):
    user_id = session.get('user_id')
    income = Income.query.filter_by(id=income_id, user_id=user_id).first()

    if not income:
        return jsonify({'status': 'error', 'message': 'Income record not found.'}), 404

    data = request.get_json() or {}

    if 'amount' in data:
        try:
            val = float(data['amount'])
            if val <= 0:
                return jsonify({'status': 'error', 'message': 'Amount must be greater than zero.'}), 400
            income.amount = val
        except (ValueError, TypeError):
            return jsonify({'status': 'error', 'message': 'Invalid amount value.'}), 400

    if 'source' in data:
        src = data['source'].strip()
        if not src:
            return jsonify({'status': 'error', 'message': 'Source cannot be empty.'}), 400
        income.source = src

    if 'date' in data:
        dt = data['date'].strip()
        if not dt:
            return jsonify({'status': 'error', 'message': 'Date cannot be empty.'}), 400
        income.date = dt

    if 'description' in data:
        income.description = data['description'].strip()

    try:
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Income record updated successfully.',
            'income': income.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to update income: {str(e)}'}), 500


@income_bp.route('/<int:income_id>', methods=['DELETE'])
@login_required
def delete_income(income_id: int):
    user_id = session.get('user_id')
    income = Income.query.filter_by(id=income_id, user_id=user_id).first()

    if not income:
        return jsonify({'status': 'error', 'message': 'Income record not found.'}), 404

    try:
        db.session.delete(income)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Income record deleted successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to delete income: {str(e)}'}), 500
