from datetime import datetime
from flask import Blueprint, request, jsonify, session
from routes.auth import login_required
from services.finance_service import FinanceService
from services.gemini_service import GeminiService, DISCLAIMER_TEXT

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')


@ai_bp.route('/status', methods=['GET'])
@login_required
def get_ai_status():
    """Checks whether the Gemini AI integration is configured."""
    is_ready = GeminiService.is_configured()
    return jsonify({
        'status': 'success',
        'is_configured': is_ready,
        'model_family': 'Google Gemini',
        'disclaimer': DISCLAIMER_TEXT
    })


@ai_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    """
    Triggers AI-powered financial advisory diagnostic using Google Gemini.
    Accepts optional month parameter (YYYY-MM).
    """
    user_id = session.get('user_id')
    data = request.get_json() or {}
    month = data.get('month')
    if not month:
        month = datetime.utcnow().strftime('%Y-%m')

    # Gather user's actual financial summary
    summary = FinanceService.get_user_dashboard_summary(user_id, target_month=month)

    # Invoke Gemini analytical service
    result = GeminiService.analyze_finances(summary)

    # Return structured response
    status_code = 200
    if result.get('status') == 'unconfigured':
        # Provide helpful guidance without crashing
        status_code = 200
    elif result.get('status') == 'error':
        status_code = 200  # Return 200 with structured error object so client displays graceful fallback UI

    return jsonify(result), status_code
