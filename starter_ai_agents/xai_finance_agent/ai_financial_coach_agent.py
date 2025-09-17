import asyncio
import json
import logging
import os
from datetime import datetime
from io import StringIO
from typing import Any, Dict, List, Literal, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

APP_NAME = "ai_financial_coach"
USER_ID = "default_user"


class SpendingCategory(BaseModel):
    category: str = Field(..., description="Expense category name")
    amount: float = Field(..., description="Total spend in this category")


class SpendingRecommendation(BaseModel):
    category: Optional[str] = Field(None, description="Category impacted by the recommendation")
    action: str = Field(..., description="Actionable guidance for the user")
    impact: Optional[str] = Field(None, description="Expected impact of the action")


class SavingsRecommendation(BaseModel):
    goal: str = Field(..., description="Savings goal or bucket")
    monthly_allocation: float = Field(..., description="Suggested monthly contribution")
    rationale: Optional[str] = Field(None, description="Reasoning behind the recommendation")


class AutomationTechnique(BaseModel):
    name: str = Field(..., description="Automation technique name")
    description: Optional[str] = Field(None, description="How to implement the technique")


class EmergencyFund(BaseModel):
    target_amount: float = Field(..., description="Recommended emergency fund size")
    recommended_monthly_savings: float = Field(..., description="Suggested monthly savings to reach the target")
    months_to_target: int = Field(..., description="Months required to hit the target")


class Debt(BaseModel):
    name: str = Field(..., description="Debt account name")
    balance: float = Field(..., description="Current outstanding balance")
    apr: float = Field(..., description="Annual percentage rate")
    minimum_payment: float = Field(..., description="Minimum monthly payment")


class DebtRecommendation(BaseModel):
    debt_name: Optional[str] = Field(None, description="Debt associated with the recommendation")
    action: str = Field(..., description="Suggested next action")
    impact: Optional[str] = Field(None, description="Expected savings or benefit")


class PayoffPlan(BaseModel):
    method: Literal["avalanche", "snowball"] = Field(..., description="Debt payoff method")
    monthly_payment: float = Field(..., description="Total monthly payment applied to debts")
    months_to_payoff: int = Field(..., description="Months needed to become debt free")
    interest_saved: float = Field(..., description="Interest saved compared with minimum payments")


class PayoffPlans(BaseModel):
    avalanche: PayoffPlan = Field(..., description="Avalanche payoff strategy details")
    snowball: PayoffPlan = Field(..., description="Snowball payoff strategy details")


class BudgetAnalysis(BaseModel):
    total_expenses: float = Field(..., description="Total monthly expenses")
    monthly_income: Optional[float] = Field(None, description="Monthly income amount")
    spending_categories: List[SpendingCategory] = Field(..., description="Breakdown of spending by category")
    recommendations: List[SpendingRecommendation] = Field(..., description="Budget optimization tips")


class SavingsStrategy(BaseModel):
    emergency_fund: EmergencyFund = Field(..., description="Emergency fund recommendation")
    recommendations: List[SavingsRecommendation] = Field(..., description="Savings allocation advice")
    automation_techniques: Optional[List[AutomationTechnique]] = Field(None, description="Automation ideas to support savings")


class DebtReduction(BaseModel):
    total_debt: float = Field(..., description="Total debt outstanding")
    debts: List[Debt] = Field(..., description="Detailed debts provided by the user")
    payoff_plans: PayoffPlans = Field(..., description="Comparison of payoff strategies")
    recommendations: Optional[List[DebtRecommendation]] = Field(None, description="Actionable debt reduction guidance")


def parse_json_safely(value: Any, fallback: Any) -> Any:
    if value is None:
        return fallback
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return fallback


def model_to_dict(model: BaseModel) -> Dict[str, Any]:
    """Return a plain dict from a Pydantic model regardless of major version."""
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


class FinanceAdvisorSystem:
    def __init__(self) -> None:
        self.session_service = InMemorySessionService()

        self.budget_analysis_agent = LlmAgent(
            name="BudgetAnalysisAgent",
            model="gemini-2.0-flash-exp",
            description="Analyzes financial data to categorize spending patterns and recommend budget improvements",
            instruction=(
                "You are a Budget Analysis Agent specialized in reviewing financial transactions and expenses. "
                "Identify spending trends, surface areas for optimization, and deliver concise recommendations."
            ),
            output_schema=BudgetAnalysis,
            output_key="budget_analysis",
        )

        self.savings_strategy_agent = LlmAgent(
            name="SavingsStrategyAgent",
            model="gemini-2.0-flash-exp",
            description="Creates personalized savings plans anchored in user goals and emergency fund needs",
            instruction=(
                "You are a Savings Strategy Agent. Create achievable savings plans, size the emergency fund, and "
                "offer automation tactics that fit the user's profile."
            ),
            output_schema=SavingsStrategy,
            output_key="savings_strategy",
        )

        self.debt_reduction_agent = LlmAgent(
            name="DebtReductionAgent",
            model="gemini-2.0-flash-exp",
            description="Builds optimized debt payoff plans using both avalanche and snowball approaches",
            instruction=(
                "You are a Debt Reduction Agent. Evaluate all debts, compare avalanche versus snowball strategies, "
                "and recommend clear next actions."
            ),
            output_schema=DebtReduction,
            output_key="debt_reduction",
        )

        self.coordinator_agent = SequentialAgent(
            name="FinanceCoordinatorAgent",
            description="Coordinates specialized finance agents to provide comprehensive financial advice",
            sub_agents=[
                self.budget_analysis_agent,
                self.savings_strategy_agent,
                self.debt_reduction_agent,
            ],
        )

        self.runner = Runner(
            agent=self.coordinator_agent,
            app_name=APP_NAME,
            session_service=self.session_service,
        )

    async def analyze_finances(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        session_id = f"finance_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        default_results = self._create_default_results(financial_data)

        try:
            session = self.session_service.create_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=session_id,
                state=financial_data.copy(),
            )

            if session.state.get("transactions"):
                self._preprocess_transactions(session)

            if session.state.get("manual_expenses"):
                self._preprocess_manual_expenses(session)

            user_content = types.Content(
                role="user",
                parts=[types.Part(text=json.dumps(session.state))],
            )

            async for event in self.runner.run_async(
                user_id=USER_ID,
                session_id=session_id,
                new_message=user_content,
            ):
                if event.is_final_response() and event.author == self.coordinator_agent.name:
                    break

            updated_session = self.session_service.get_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=session_id,
            )

            results: Dict[str, Any] = {}
            for key in ["budget_analysis", "savings_strategy", "debt_reduction"]:
                value = updated_session.state.get(key)
                results[key] = parse_json_safely(value, default_results[key]) if value else default_results[key]

            return results
        except Exception:
            logging.exception("Finance advisor pipeline failed; returning defaults")
            return default_results
        finally:
            self.session_service.delete_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=session_id,
            )

    def _preprocess_transactions(self, session: Any) -> None:
        transactions = session.state.get("transactions", [])
        if not transactions:
            return

        df = pd.DataFrame(transactions)
        if not {"Date", "Category", "Amount"}.issubset(df.columns):
            return

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        df = df.dropna(subset=["Amount"])

        category_totals = df.groupby("Category")["Amount"].sum().reset_index()

        session.state["transactions"] = df.sort_values("Date").to_dict("records")
        session.state["category_totals"] = category_totals.to_dict("records")
        session.state["total_expenses"] = float(df["Amount"].sum())

    def _preprocess_manual_expenses(self, session: Any) -> None:
        manual = session.state.get("manual_expenses", {}) or {}
        if not manual:
            return

        transactions = session.state.get("transactions", [])
        today = datetime.now().strftime("%Y-%m-%d")
        for category, amount in manual.items():
            transactions.append({"Date": today, "Category": category, "Amount": float(amount)})

        session.state["transactions"] = transactions
        self._preprocess_transactions(session)

    def _create_default_results(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        monthly_income = float(financial_data.get("monthly_income") or 0.0)
        transactions = financial_data.get("transactions", []) or []
        manual_expenses = financial_data.get("manual_expenses", {}) or {}
        debts_input = financial_data.get("debts", []) or []

        category_totals: Dict[str, float] = {}
        for txn in transactions:
            category = str(txn.get("Category", "Uncategorized"))
            amount = float(txn.get("Amount") or 0.0)
            category_totals[category] = category_totals.get(category, 0.0) + amount
        for category, amount in manual_expenses.items():
            category_totals[category] = category_totals.get(category, 0.0) + float(amount)

        spending_categories = [
            model_to_dict(SpendingCategory(category=category, amount=amount))
            for category, amount in category_totals.items()
        ]
        total_expenses = sum(category_totals.values())

        emergency_target = max(monthly_income * 3, total_expenses)
        emergency_monthly = emergency_target / 12 if emergency_target else 0.0
        emergency_months = 12 if emergency_monthly else 0

        debts = [
            model_to_dict(
                Debt(
                    name=str(debt.get("name", "")),
                    balance=float(debt.get("balance", 0.0) or 0.0),
                    apr=float(debt.get("apr", 0.0) or 0.0),
                    minimum_payment=float(debt.get("minimum_payment", 0.0) or 0.0),
                )
            )
            for debt in debts_input
            if str(debt.get("name", ""))
        ]
        total_debt = sum(item["balance"] for item in debts)

        avalanche_plan = PayoffPlan(
            method="avalanche",
            monthly_payment=0.0,
            months_to_payoff=0,
            interest_saved=0.0,
        )
        snowball_plan = PayoffPlan(
            method="snowball",
            monthly_payment=0.0,
            months_to_payoff=0,
            interest_saved=0.0,
        )

        budget_analysis_model = BudgetAnalysis(
            total_expenses=total_expenses,
            monthly_income=monthly_income,
            spending_categories=spending_categories,
            recommendations=[],
        )
        savings_strategy_model = SavingsStrategy(
            emergency_fund=EmergencyFund(
                target_amount=emergency_target,
                recommended_monthly_savings=emergency_monthly,
                months_to_target=emergency_months,
            ),
            recommendations=[],
            automation_techniques=[],
        )
        debt_reduction_model = DebtReduction(
            total_debt=total_debt,
            debts=debts,
            payoff_plans=PayoffPlans(
                avalanche=avalanche_plan,
                snowball=snowball_plan,
            ),
            recommendations=[],
        )

        return {
            "budget_analysis": model_to_dict(budget_analysis_model),
            "savings_strategy": model_to_dict(savings_strategy_model),
            "debt_reduction": model_to_dict(debt_reduction_model),
        }


def parse_csv_transactions(file_content: bytes) -> Dict[str, Any]:
    try:
        df = pd.read_csv(StringIO(file_content.decode("utf-8")))
    except UnicodeDecodeError:
        df = pd.read_csv(StringIO(file_content.decode("latin-1")))

    required_columns = {"Date", "Category", "Amount"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing_columns))}")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["Amount"] = (
        df["Amount"].astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False).astype(float)
    )

    category_totals = df.groupby("Category")["Amount"].sum().reset_index()

    return {
        "transactions": df.to_dict("records"),
        "category_totals": category_totals.to_dict("records"),
    }


def display_budget_analysis(analysis: Dict[str, Any]) -> None:
    st.subheader("Budget Analysis")

    categories = analysis.get("spending_categories", []) or []
    if categories:
        fig = px.pie(
            values=[item["amount"] for item in categories],
            names=[item["category"] for item in categories],
            title="Spending Breakdown",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Provide transactions or manual expenses to see a spending breakdown.")

    total_expenses = analysis.get("total_expenses", 0.0) or 0.0
    income = analysis.get("monthly_income", 0.0) or 0.0
    if total_expenses or income:
        fig = go.Figure()
        fig.add_trace(
            go.Bar(x=["Income", "Expenses"], y=[income, total_expenses], marker_color=["green", "red"])
        )
        fig.update_layout(title="Monthly Income vs Expenses")
        st.plotly_chart(fig, use_container_width=True)

    recommendations = analysis.get("recommendations", []) or []
    if recommendations:
        st.markdown("**Recommendations**")
        for item in recommendations:
            category = item.get("category")
            impact = item.get("impact")
            bullet = item.get("action", "")
            if category:
                bullet = f"[{category}] {bullet}"
            if impact:
                bullet = f"{bullet} — {impact}"
            st.write(f"- {bullet}")


def display_savings_strategy(strategy: Dict[str, Any]) -> None:
    st.subheader("Savings Strategy")

    emergency = strategy.get("emergency_fund", {})
    if emergency:
        st.metric("Emergency Fund Target", f"${emergency.get('target_amount', 0):,.2f}")
        st.metric("Monthly Savings", f"${emergency.get('recommended_monthly_savings', 0):,.2f}")
        st.metric("Months to Target", emergency.get("months_to_target", 0))

    recommendations = strategy.get("recommendations", []) or []
    if recommendations:
        st.markdown("**Savings Allocations**")
        for rec in recommendations:
            goal = rec.get("goal", "Savings Goal")
            amount = rec.get("monthly_allocation", 0.0)
            rationale = rec.get("rationale")
            line = f"- {goal}: ${amount:,.2f} per month"
            if rationale:
                line = f"{line} ({rationale})"
            st.write(line)

    automation = strategy.get("automation_techniques", []) or []
    if automation:
        st.markdown("**Automation Ideas**")
        for item in automation:
            description = item.get("description")
            line = f"- {item.get('name', 'Automation')}"
            if description:
                line = f"{line}: {description}"
            st.write(line)


def display_debt_reduction(debt_strategy: Dict[str, Any]) -> None:
    st.subheader("Debt Reduction")

    total_debt = debt_strategy.get("total_debt", 0.0)
    st.metric("Total Debt", f"${total_debt:,.2f}")

    debts = debt_strategy.get("debts", []) or []
    if debts:
        debt_df = pd.DataFrame(debts)
        st.dataframe(debt_df)

    payoff_plans = debt_strategy.get("payoff_plans", {}) or {}
    if payoff_plans:
        plan_rows = []
        for method, plan in payoff_plans.items():
            if isinstance(plan, dict):
                plan_rows.append(
                    {
                        "Method": method.title(),
                        "Monthly Payment": plan.get("monthly_payment", 0.0),
                        "Months to Payoff": plan.get("months_to_payoff", 0),
                        "Interest Saved": plan.get("interest_saved", 0.0),
                    }
                )
        if plan_rows:
            plan_df = pd.DataFrame(plan_rows)
            st.table(plan_df.style.format({"Monthly Payment": "${:,.2f}", "Interest Saved": "${:,.2f}"}))

    recommendations = debt_strategy.get("recommendations", []) or []
    if recommendations:
        st.markdown("**Action Plan**")
        for rec in recommendations:
            debt_name = rec.get("debt_name")
            line = f"- {rec.get('action', '')}"
            if debt_name:
                line = f"{line} ({debt_name})"
            impact = rec.get("impact")
            if impact:
                line = f"{line} — {impact}"
            st.write(line)


def main() -> None:
    st.set_page_config(
        page_title="AI Financial Coach",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("AI Financial Coach")
    st.caption("Powered by Google ADK and Gemini")

    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        st.error("Set GOOGLE_API_KEY in a .env file before running the app.")
        return

    financial_system = FinanceAdvisorSystem()

    with st.sidebar:
        st.header("Setup & Templates")
        st.info("Store your Gemini API key in a .env file as GOOGLE_API_KEY=your_key_here")
        st.markdown("**CSV Requirements**")
        st.write("Date (YYYY-MM-DD), Category, Amount")
        sample_csv = (
            "Date,Category,Amount\n"
            "2024-01-01,Housing,1200.00\n"
            "2024-01-02,Food,150.50\n"
            "2024-01-03,Transportation,45.00"
        )
        st.download_button(
            label="Download CSV Template",
            data=sample_csv,
            file_name="expense_template.csv",
            mime="text/csv",
        )

    uploaded_file = st.file_uploader("Upload transactions CSV", type=["csv"])
    transactions_from_csv: List[Dict[str, Any]] = []
    category_totals_from_csv: List[Dict[str, Any]] = []
    if uploaded_file is not None:
        try:
            parsed = parse_csv_transactions(uploaded_file.getvalue())
            transactions_from_csv = parsed["transactions"]
            category_totals_from_csv = parsed["category_totals"]
            st.success("Transactions loaded from CSV.")
        except ValueError as exc:
            st.error(str(exc))

    default_expenses = pd.DataFrame([{"Category": "", "Amount": 0.0}])
    default_debts = pd.DataFrame(
        [{"name": "", "balance": 0.0, "apr": 0.0, "minimum_payment": 0.0}]
    )

    with st.form("financial_inputs"):
        monthly_income = st.number_input("Monthly Income", min_value=0.0, step=100.0)
        dependants = st.number_input("Dependants", min_value=0, step=1)

        st.markdown("**Manual Expenses**")
        manual_expense_rows = st.data_editor(
            default_expenses,
            column_config={
                "Category": st.column_config.TextColumn(required=False),
                "Amount": st.column_config.NumberColumn(format="%0.2f", min_value=0.0),
            },
            num_rows="dynamic",
        )

        st.markdown("**Debts**")
        debt_rows = st.data_editor(
            default_debts,
            column_config={
                "name": st.column_config.TextColumn(label="Name"),
                "balance": st.column_config.NumberColumn(label="Balance", format="%0.2f", min_value=0.0),
                "apr": st.column_config.NumberColumn(label="APR %", format="%0.2f", min_value=0.0),
                "minimum_payment": st.column_config.NumberColumn(
                    label="Minimum Payment", format="%0.2f", min_value=0.0
                ),
            },
            num_rows="dynamic",
        )

        submitted = st.form_submit_button("Analyze My Finances")

    if not submitted:
        return

    manual_expenses = {
        row["Category"]: float(row["Amount"])
        for _, row in manual_expense_rows.dropna(subset=["Category", "Amount"]).iterrows()
        if str(row["Category"]).strip() and float(row["Amount"])
    }

    debts = []
    for _, row in debt_rows.iterrows():
        name = str(row.get("name", "")).strip()
        if not name:
            continue
        debts.append(
            {
                "name": name,
                "balance": float(row.get("balance", 0.0) or 0.0),
                "apr": float(row.get("apr", 0.0) or 0.0),
                "minimum_payment": float(row.get("minimum_payment", 0.0) or 0.0),
            }
        )

    financial_data = {
        "monthly_income": monthly_income,
        "dependants": dependants,
        "transactions": transactions_from_csv,
        "category_totals": category_totals_from_csv,
        "manual_expenses": manual_expenses,
        "debts": debts,
    }

    with st.spinner("Analyzing your finances..."):
        results = asyncio.run(financial_system.analyze_finances(financial_data))

    budget_tab, savings_tab, debt_tab = st.tabs(["Budget", "Savings", "Debt"])

    with budget_tab:
        display_budget_analysis(results.get("budget_analysis", {}))
    with savings_tab:
        display_savings_strategy(results.get("savings_strategy", {}))
    with debt_tab:
        display_debt_reduction(results.get("debt_reduction", {}))


if __name__ == "__main__":
    main()
