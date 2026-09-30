import os
import json
import logging
from config import Config

logger = logging.getLogger(__name__)

DISCLAIMER_TEXT = (
    "AI-generated information is for educational and planning purposes and should "
    "not be considered professional financial advice."
)


class GeminiService:
    """Service to generate financial insights via Google Gemini."""

    @classmethod
    def is_configured(cls) -> bool:
        """Check if Gemini API key is configured."""
        key = Config.GEMINI_API_KEY or os.environ.get('GEMINI_API_KEY', '')
        return bool(key and key.strip() and key != 'your_gemini_api_key_here')

    @classmethod
    def analyze_finances(cls, finance_summary: dict) -> dict:
        """
        Takes structured financial summary dictionary and returns AI insights.
        Returns a dictionary with status, insights, and disclaimer.
        """
        api_key = Config.GEMINI_API_KEY or os.environ.get('GEMINI_API_KEY', '').strip()

        if not api_key or api_key == 'your_gemini_api_key_here':
            return {
                'status': 'unconfigured',
                'title': 'Gemini API Key Required',
                'message': (
                    'Google Gemini API key is not configured. '
                    'To enable AI financial diagnostics, add your GEMINI_API_KEY in the .env file and restart the application.'
                ),
                'disclaimer': DISCLAIMER_TEXT,
                'insights': None
            }

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)

            # Build prompt
            prompt = cls._build_prompt(finance_summary)

            # Available models to try in sequence
            models_to_try = [
                'gemini-3.8-flash',
                'gemini-2.5-flash',
                'gemini-2.0-flash',
                'gemini-1.5-flash'
            ]

            last_error = None
            response_text = None

            for model_name in models_to_try:
                try:
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        generation_config={
                            'temperature': 0.3,
                            'top_p': 0.85,
                            'max_output_tokens': 2048,
                        }
                    )
                    response = model.generate_content(prompt)
                    if response and response.text:
                        response_text = response.text
                        break
                except Exception as ex:
                    last_error = ex
                    logger.warning(f"Failed with model {model_name}: {ex}")
                    continue

            if not response_text:
                raise Exception(f"Unable to generate response from Gemini: {last_error}")

            # Parse or format the response
            parsed_insights = cls._parse_or_structure_response(response_text)

            return {
                'status': 'success',
                'title': 'Personalized Financial Analysis',
                'insights': parsed_insights,
                'raw_markdown': response_text,
                'disclaimer': DISCLAIMER_TEXT
            }

        except Exception as e:
            logger.error(f"Gemini API error: {e}", exc_info=True)
            return {
                'status': 'error',
                'title': 'AI Advisory Service Unavailable',
                'message': f"Encountered an issue communicating with the AI service: {str(e)}",
                'disclaimer': DISCLAIMER_TEXT,
                'insights': None
            }

    @classmethod
    def _build_prompt(cls, summary: dict) -> str:
        """Constructs an analytical prompt with Indian Rupee figures."""
        total_inc = summary.get('total_income', 0.0)
        total_exp = summary.get('total_expense', 0.0)
        savings = summary.get('savings', 0.0)
        savings_pct = summary.get('savings_percentage', 0.0)
        categories = summary.get('category_spending', {})
        budgets = summary.get('budget_comparison', [])
        goals = summary.get('goals', [])
        month = summary.get('target_month', 'Current Month')

        categories_formatted = "\n".join([f"  - {cat}: ₹{amt:,.2f}" for cat, amt in categories.items()]) or "  None recorded"

        budget_formatted = []
        for b in budgets:
            budget_formatted.append(
                f"  - {b.get('category')}: Limit ₹{b.get('limit', 0):,.2f}, Spent ₹{b.get('spent', 0):,.2f}, "
                f"Remaining ₹{b.get('remaining', 0):,.2f} ({b.get('status', 'ok')})"
            )
        budget_str = "\n".join(budget_formatted) or "  No budget limits established"

        goals_formatted = []
        for g in goals:
            goals_formatted.append(
                f"  - {g.get('name')}: Current ₹{g.get('current_amount', 0):,.2f} / Target ₹{g.get('target_amount', 0):,.2f} "
                f"(Target Date: {g.get('target_date', 'N/A')})"
            )
        goals_str = "\n".join(goals_formatted) or "  No savings goals configured"

        prompt = f"""
You are the AI Financial Advisor Bot within an institutional personal cash flow management system.
The user is tracking finances in Indian Rupees (INR / ₹).

Here is the user's financial profile for period {month}:
- Total Monthly Income: ₹{total_inc:,.2f}
- Total Monthly Expenses: ₹{total_exp:,.2f}
- Net Monthly Savings: ₹{savings:,.2f}
- Savings Ratio: {savings_pct}%
- Category Breakdown:
{categories_formatted}
- Category Budgets:
{budget_str}
- Active Savings Goals:
{goals_str}

CRITICAL RULES:
1. All monetary numbers must be denoted with the Indian Rupee symbol (₹).
2. Do NOT use em dashes (—). Use hyphens (-), colons, or clean phrasing.
3. Do NOT use emoji icons anywhere in your text.
4. Tone must be professional, direct, analytical, and practical. Do not use generic buzzwords.
5. Provide realistic, data-grounded assessments based strictly on the figures provided.
6. The AI must NOT pretend to be a licensed financial advisor. Do not recommend specific stocks, mutual funds, or automated trading.
7. Structure your analysis into the following 5 clean markdown sections with ## headers:
   ## 1. Executive Cash Flow Diagnostic
   ## 2. Category Variance and Leakage Analysis
   ## 3. Budget Rebalancing Recommendations
   ## 4. Savings and Expense Optimization Strategies
   ## 5. Practical 30-Day Financial Plan

End with this exact disclaimer:
"AI-generated information is for educational and planning purposes and should not be considered professional financial advice."
"""
        return prompt.strip()

    @classmethod
    def _parse_or_structure_response(cls, text: str) -> dict:
        """Parses markdown response into clean structured sections."""
        sections = {}
        current_section = "Executive Financial Diagnostic"
        lines = text.split("\n")
        section_lines = []

        for line in lines:
            stripped = line.strip()
            # Match ## Header or ### Header or **1. Header**
            if stripped.startswith("## ") or stripped.startswith("### "):
                if section_lines:
                    cleaned_content = "\n".join(section_lines).strip()
                    if cleaned_content:
                        sections[current_section] = cleaned_content
                    section_lines = []
                current_section = stripped.lstrip("#").strip()
            elif stripped.startswith("**") and stripped.endswith("**") and len(stripped) < 80:
                if section_lines:
                    cleaned_content = "\n".join(section_lines).strip()
                    if cleaned_content:
                        sections[current_section] = cleaned_content
                    section_lines = []
                current_section = stripped.strip("*").strip()
            else:
                section_lines.append(line)

        if section_lines:
            cleaned_content = "\n".join(section_lines).strip()
            if cleaned_content:
                sections[current_section] = cleaned_content

        # If parsing resulted in only 1 block, return the text directly
        if len(sections) <= 1:
            sections = {"Financial Advisory Diagnostic": text.strip()}

        return sections
