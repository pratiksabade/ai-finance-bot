from datetime import datetime
from flask import Blueprint, request, jsonify, session
from models import db, SavingsGoal
from routes.auth import login_required

goals_bp = Blueprint('goals', __name__, url_prefix='/api/goals')


@goals_bp.route('', methods=['GET'])
@login_required
def list_goals():
    user_id = session.get('user_id')
    goals = SavingsGoal.query.filter_by(user_id=user_id).order_by(SavingsGoal.target_date.asc()).all()

    total_target = sum(g.target_amount for g in goals)
    total_saved = sum(g.current_amount for g in goals)
    progress_pct = round((total_saved / total_target * 100), 1) if total_target > 0 else 0.0

    return jsonify({
        'status': 'success',
        'count': len(goals),
        'total_target': round(total_target, 2),
        'total_saved': round(total_saved, 2),
        'progress_percentage': progress_pct,
        'goals': [g.to_dict() for g in goals]
    })


@goals_bp.route('', methods=['POST'])
@login_required
def add_goal():
    user_id = session.get('user_id')
    data = request.get_json() or {}

    name = data.get('name', '').strip()
    target_date = data.get('target_date', '').strip()

    try:
        target_amount = float(data.get('target_amount', 0))
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'Invalid target amount.'}), 400

    try:
        current_amount = float(data.get('current_amount', 0))
    except (ValueError, TypeError):
        current_amount = 0.0

    if not name:
        return jsonify({'status': 'error', 'message': 'Goal name is required.'}), 400
    if target_amount <= 0:
        return jsonify({'status': 'error', 'message': 'Target amount must be greater than zero.'}), 400
    if not target_date:
        return jsonify({'status': 'error', 'message': 'Target completion date is required.'}), 400

    try:
        new_goal = SavingsGoal(
            user_id=user_id,
            name=name,
            target_amount=target_amount,
            current_amount=max(0.0, current_amount),
            target_date=target_date
        )
        db.session.add(new_goal)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': f'Savings goal "{name}" established.',
            'goal': new_goal.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to create savings goal: {str(e)}'}), 500


@goals_bp.route('/<int:goal_id>', methods=['PUT'])
@login_required
def update_goal(goal_id: int):
    user_id = session.get('user_id')
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=user_id).first()

    if not goal:
        return jsonify({'status': 'error', 'message': 'Savings goal not found.'}), 404

    data = request.get_json() or {}

    if 'name' in data:
        name_val = data['name'].strip()
        if not name_val:
            return jsonify({'status': 'error', 'message': 'Goal name cannot be empty.'}), 400
        goal.name = name_val

    if 'target_amount' in data:
        try:
            val = float(data['target_amount'])
            if val <= 0:
                return jsonify({'status': 'error', 'message': 'Target amount must be greater than zero.'}), 400
            goal.target_amount = val
        except (ValueError, TypeError):
            return jsonify({'status': 'error', 'message': 'Invalid target amount.'}), 400

    if 'current_amount' in data:
        try:
            val = float(data['current_amount'])
            if val < 0:
                return jsonify({'status': 'error', 'message': 'Current amount cannot be negative.'}), 400
            goal.current_amount = val
        except (ValueError, TypeError):
            return jsonify({'status': 'error', 'message': 'Invalid current amount.'}), 400

    if 'target_date' in data:
        dt = data['target_date'].strip()
        if not dt:
            return jsonify({'status': 'error', 'message': 'Target date cannot be empty.'}), 400
        goal.target_date = dt

    try:
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Savings goal updated successfully.',
            'goal': goal.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to update savings goal: {str(e)}'}), 500


@goals_bp.route('/<int:goal_id>/deposit', methods=['POST'])
@login_required
def deposit_to_goal(goal_id: int):
    """Add funds towards an existing savings goal."""
    user_id = session.get('user_id')
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=user_id).first()

    if not goal:
        return jsonify({'status': 'error', 'message': 'Savings goal not found.'}), 404

    data = request.get_json() or {}
    try:
        amount = float(data.get('amount', 0))
        if amount <= 0:
            return jsonify({'status': 'error', 'message': 'Deposit amount must be greater than zero.'}), 400
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'Invalid deposit amount.'}), 400

    try:
        goal.current_amount = float(goal.current_amount) + amount
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': f'Allocated ₹{amount:,.2f} to {goal.name}.',
            'goal': goal.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Deposit failed: {str(e)}'}), 500


@goals_bp.route('/<int:goal_id>', methods=['DELETE'])
@login_required
def delete_goal(goal_id: int):
    user_id = session.get('user_id')
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=user_id).first()

    if not goal:
        return jsonify({'status': 'error', 'message': 'Savings goal not found.'}), 404

    try:
        db.session.delete(goal)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Savings goal deleted successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to delete goal: {str(e)}'}), 500
