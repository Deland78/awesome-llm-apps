## 📊 Build a Multi-Agent Personal Finance Coach
Fully functional multi-agent app with step-by-step instructions (100% opensource)

This Streamlit application implements a comprehensive financial advisory system using Google's Agent Development Kit (ADK) with multiple specialized AI agents.

### Features
👬 Multi-Agent Financial Analysis System

Budget Analysis Agent: Analyzes spending patterns and recommends optimizations

Savings Strategy Agent: Creates personalized savings plans and emergency fund strategies

Debt Reduction Agent: Develops optimized debt payoff strategies using avalanche and snowball methods

🫰 Expense Analysis:

Supports both CSV upload and manual expense entry

Visual breakdown of spending by category

Automated expense categorization and pattern detection

💰 Savings Recommendations:

Emergency fund sizing and building strategies

Custom savings allocations across different goals

💸 Debt Management:

Multiple debt handling with interest rate optimization

Comparison between avalanche and snowball methods

Visual debt payoff timeline and interest savings analysis

Actionable debt reduction recommendations

📊 Interactive Visualizations:

Pie charts for expense breakdown

Bar charts for income vs. expenses

Debt comparison graphs
The application follows a multi-agent coordination pattern typical of complex AI systems:

Data Collection: Users enter financial information (income, expenses, debts) through the Streamlit interface, either manually or via CSV upload.

Agent Chain Execution: The app uses SequentialAgent, a workflow agent that executes its sub-agents in the order they are specified in the list:

Budget Analysis Agent evaluates spending patterns and identifies areas for reduction

Savings Strategy Agent develops savings plans based on budget analysis

Debt Reduction Agent creates optimized debt payoff strategies using both analytical methods

State Management: Each agent stores its results in the shared session state, allowing subsequent agents to build upon prior analysis. This state-passing mechanism enables a coherent analysis pipeline without duplicating work.

Visualization: The application processes agent outputs into interactive visualizations using Plotly, making complex financial insights accessible and actionable.

### How to get Started?

1. Clone the GitHub repository
```bash
git clone https://github.com/Shubhamsaboo/awesome-llm-apps.git
cd awesome-llm-apps/ai_agent_tutorials/xai_finance_agent
```

2. Install the required dependencies:

```bash
cd awesome-llm-apps/ai_agent_tutorials/xai_finance_agent
pip install -r requirements.txt
```

3. Get your OpenAI API Key

- Sign up for an [xAI API account](https://console.x.ai/)
- Set your XAI_API_KEY environment variable.
```bash
export XAI_API_KEY='your-api-key-here'
```

4. Build and Run the team of AI Agents
   see: https://www.theunwindai.com/p/build-a-multi-agent-personal-finance-coach)

6. Open your web browser and navigate to the URL provided in the console output to interact with the AI financial agent through the playground interface.
