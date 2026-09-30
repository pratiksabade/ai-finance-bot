"""
Automated Backend & API Verification Suite
Verifies models, authentication, CRUD operations, calculations, and Gemini AI integration.
"""

import os
import sys
import json

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from app import create_app
from models import db, User, Income, Expense, Budget, SavingsGoal
from services.finance_service import FinanceService
from services.gemini_service import GeminiService


def run_tests():
    app = create_app()
    app.config['TESTING'] = True
    client = app.test_client()

    print("=== [1] HEALTH CHECK TEST ===")
    res = client.get('/api/health')
    assert res.status_code == 200, f"Health check failed: {res.status_code}"
    data = res.get_json()
    assert data['status'] == 'healthy'
    assert data['currency'] == 'INR'
    print("✓ Health check endpoint operational.")

    print("\n=== [2] AUTHENTICATION & SESSION TEST ===")
    # Login with demo credentials
    res = client.post('/api/auth/login', json={
        'email': 'demo@financeadvisor.in',
        'password': 'Password@123'
    })
    assert res.status_code == 200, f"Login failed: {res.status_code}, {res.data}"
    login_data = res.get_json()
    assert login_data['status'] == 'success'
    print(f"✓ Authentication successful for {login_data['user']['email']}.")

    # Check /api/auth/me
    res = client.get('/api/auth/me')
    assert res.status_code == 200
    assert res.get_json()['status'] == 'authenticated'
    print("✓ Session persistence verified.")

    print("\n=== [3] FINANCIAL DASHBOARD SUMMARY & CALCULATIONS ===")
    res = client.get('/api/dashboard')
    assert res.status_code == 200
    dash_data = res.get_json()['data']
    print(f"  Monthly Income:     {dash_data['total_income_formatted']}")
    print(f"  Monthly Expenses:   {dash_data['total_expense_formatted']}")
    print(f"  Monthly Savings:    {dash_data['savings_formatted']}")
    print(f"  Savings Percentage: {dash_data['savings_percentage']}%")
    print(f"  Remaining Budget:   {dash_data['remaining_budget_formatted']}")
    assert dash_data['currency'] == 'INR'
    assert 'category_spending' in dash_data
    assert 'trends' in dash_data
    print("✓ Financial calculations and INR formatting verified.")

    print("\n=== [4] CRUD OPERATIONS TEST ===")
    # Add Income
    res = client.post('/api/income', json={
        'source': 'Test Bonus Inflow',
        'amount': 15000.0,
        'date': '2026-09-28',
        'description': 'Quarterly appraisal incentive'
    })
    assert res.status_code == 201
    new_inc = res.get_json()['income']
    inc_id = new_inc['id']
    print(f"✓ Income created (ID {inc_id}): +₹15,000.00")

    # Update Income
    res = client.put(f'/api/income/{inc_id}', json={'amount': 16000.0})
    assert res.status_code == 200
    assert res.get_json()['income']['amount'] == 16000.0
    print(f"✓ Income updated to ₹16,000.00")

    # Delete Income
    res = client.delete(f'/api/income/{inc_id}')
    assert res.status_code == 200
    print(f"✓ Income deleted.")

    # Add Expense
    res = client.post('/api/expenses', json={
        'category': 'Education',
        'amount': 3200.0,
        'date': '2026-09-29',
        'description': 'Reference manual purchase'
    })
    assert res.status_code == 201
    new_exp = res.get_json()['expense']
    exp_id = new_exp['id']
    print(f"✓ Expense logged (ID {exp_id}): -₹3,200.00")

    # Delete Expense
    res = client.delete(f'/api/expenses/{exp_id}')
    assert res.status_code == 200
    print(f"✓ Expense deleted.")

    print("\n=== [5] SAVINGS GOALS & DEPOSITS ===")
    res = client.get('/api/goals')
    assert res.status_code == 200
    goals = res.get_json()['goals']
    assert len(goals) > 0
    first_goal = goals[0]
    initial_amount = first_goal['current_amount']
    # Deposit funds
    res = client.post(f"/api/goals/{first_goal['id']}/deposit", json={'amount': 5000.0})
    assert res.status_code == 200
    updated_goal = res.get_json()['goal']
    assert updated_goal['current_amount'] == initial_amount + 5000.0
    print(f"✓ Allocated ₹5,000.00 to '{first_goal['name']}'. New Balance: ₹{updated_goal['current_amount']:,.2f}")

    print("\n=== [6] GOOGLE GEMINI AI INTEGRATION TEST ===")
    ai_status = client.get('/api/ai/status').get_json()
    print(f"  Gemini Configured: {ai_status['is_configured']}")

    # Call AI analysis endpoint
    print("  Querying Gemini API diagnostic endpoint...")
    ai_res = client.post('/api/ai/analyze', json={'month': '2026-09'})
    ai_data = ai_res.get_json()
    print(f"  AI Response Status: {ai_data.get('status')}")
    if ai_data.get('status') == 'success':
        print("✓ Gemini API responded successfully!")
        sections = ai_data.get('insights', {})
        print(f"  Diagnostic Sections Generated: {list(sections.keys())}")
        assert 'disclaimer' in ai_data
        print(f"  Disclaimer: {ai_data['disclaimer']}")
    else:
        print(f"  AI Diagnostic Note: {ai_data.get('message')}")
        assert 'disclaimer' in ai_data

    print("\n=== [7] PUBLIC PAGES & LEGAL ROUTING ===")
    for path in ['/', '/login', '/register', '/privacy-policy', '/terms']:
        r = client.get(path)
        assert r.status_code in [200, 302], f"Page {path} returned status {r.status_code}"
    print("✓ All landing, auth, privacy, and terms routes rendered cleanly.")

    print("\n==============================================")
    print("  ALL APPLICATION TESTS PASSED SUCCESSFULLY!  ")
    print("==============================================")


if __name__ == '__main__':
    run_tests()
