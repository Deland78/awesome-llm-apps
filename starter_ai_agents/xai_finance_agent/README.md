## AI Financial Coach Agent with Google ADK
The AI Financial Coach is a personalized financial advisor powered by Google's Agent Development Kit (ADK). It coordinates a team of Gemini agents to analyze budgets, craft savings plans, and optimize debt payoff strategies based on the data you provide.

### Features
- Budget Analysis Agent highlights spending patterns and offers optimization tips
- Savings Strategy Agent sizes an emergency fund, recommends allocations, and suggests automation tactics
- Debt Reduction Agent compares avalanche and snowball paydown plans with actionable next steps
- CSV ingestion plus manual expense entry, backed by Plotly charts for spending and income vs. expense comparisons
- Streamlit UI with tabbed insights for budget, savings, and debt views

### How It Works
1. **Data collection** – Supply monthly income, dependants, optional CSV transactions, manual expenses, and debts via the Streamlit interface.
2. **Agent chain** – A `SequentialAgent` executes the Budget, Savings, and Debt specialists in order, sharing results through the ADK session state.
3. **Visualization** – The app renders the agent output as interactive charts and tables so financial recommendations are easy to act on.

### Getting Started
1. **Clone the repository**
   ```bash
   git clone https://github.com/Shubhamsaboo/awesome-llm-apps.git
   cd awesome-llm-apps/starter_ai_agents/xai_finance_agent
   ```
2. **Configure your Gemini API key**
   ```bash
   cp .env.example .env
   # edit .env and set GOOGLE_API_KEY=your_api_key_here
   ```
   Grab a free key from Google AI Studio: https://aistudio.google.com/apikey
3. **Install dependencies**
   ```bash
   python -m pip install -r requirements.txt
   ```
4. **Run the Streamlit app**
   ```bash
   streamlit run ai_financial_coach_agent.py
   ```

### CSV File Format
| Column   | Description                       |
|----------|-----------------------------------|
| Date     | Transaction date (YYYY-MM-DD)     |
| Category | Expense category label            |
| Amount   | Transaction amount (numbers only) |

Example:
```text
Date,Category,Amount
2024-01-01,Housing,1200.00
2024-01-02,Food,150.50
2024-01-03,Transportation,45.00
```
A matching template is available from the app sidebar.

### Usage Tips
- Combine CSV uploads with manual expenses to capture cash or ad-hoc spending.
- Enter every outstanding debt with balance, APR, and minimum payment to unlock payoff projections.
- Review the Budget, Savings, and Debt tabs after each submission to track recommendations and progress.
