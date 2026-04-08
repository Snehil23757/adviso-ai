import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
from sklearn.linear_model import LinearRegression
import numpy as np
import time

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Adviso AI", layout="wide")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------- UI ----------------
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#020617,#0f172a);color:#e2e8f0;}
.title {
    font-size:40px;font-weight:900;text-align:center;
    background:linear-gradient(90deg,#38bdf8,#6366f1,#22c55e);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🚀 Adviso AI</div>", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "users" not in st.session_state:
    st.session_state.users = {"admin": "1234"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "history" not in st.session_state:
    st.session_state.history = []

if "last_call" not in st.session_state:
    st.session_state.last_call = 0

# ---------------- FUNCTIONS ----------------
def can_call():
    return time.time() - st.session_state.last_call > 5

def safe_ai(messages):
    try:
        if not can_call():
            return "⏳ Wait a few seconds"
        st.session_state.last_call = time.time()
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"⚠️ {str(e)}"

def save_history(title, content):
    st.session_state.history.append({"title": title, "content": content})

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 👤 Profile")

if not st.session_state.logged_in:
    mode = st.sidebar.radio("Login / Signup", ["Login", "Signup"])
    user = st.sidebar.text_input("Username")
    pwd = st.sidebar.text_input("Password", type="password")

    if mode == "Login":
        if st.sidebar.button("Login"):
            if user in st.session_state.users and st.session_state.users[user] == pwd:
                st.session_state.logged_in = True
                st.success("Logged in")
            else:
                st.error("Invalid credentials")
    else:
        if st.sidebar.button("Signup"):
            st.session_state.users[user] = pwd
            st.success("Account created")
else:
    st.sidebar.success("Logged in")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False

# ---------------- HISTORY ----------------
st.sidebar.markdown("## 📜 History")

if len(st.session_state.history) == 0:
    st.sidebar.info("No history yet")
else:
    for i, h in enumerate(reversed(st.session_state.history)):
        if st.sidebar.button(f"{h['title']} {i}"):
            st.sidebar.write(h["content"])

# ---------------- BLOCK ----------------
if not st.session_state.logged_in:
    st.warning("🔐 Please login")
    st.stop()

# ---------------- FILE ----------------
file = st.sidebar.file_uploader("Upload Data", type=["csv","xlsx"])

# ---------------- MAIN ----------------
if file:
    data = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs(
        ["📊 Overview","📈 Charts","🧠 AI","🤖 Chat","💡 Ideas","💰 Profit","📈 Forecast","💰 Budget","🌱 Sustainability","📊 Competitor","📊 KPI"]
    )

    # ---------- OVERVIEW ----------
    with tab1:
        st.metric("Rows", data.shape[0])
        st.metric("Columns", data.shape[1])

        missing = data.isnull().sum()
        percent = (missing / len(data)) * 100

        st.dataframe(pd.DataFrame({
            "Column": missing.index,
            "Missing": missing.values,
            "%": percent.values
        }))

        st.bar_chart(missing)

        with st.expander("Full Data"):
            st.dataframe(data)

        st.dataframe(data.head())

        stats = data.describe()
        st.dataframe(stats)

    # ---------- CHARTS ----------
    with tab2:
        chart = st.selectbox("Chart", ["Scatter","Line","Bar","Histogram"])
        x = st.selectbox("X", data.columns)
        y = st.selectbox("Y", data.select_dtypes(include=['int64','float64']).columns)

        filtered = data.copy()

        cat_cols = data.select_dtypes(include=['object']).columns
        if len(cat_cols)>0:
            cat = st.selectbox("Category", ["None"]+list(cat_cols))
            if cat!="None":
                vals = st.multiselect("Values", data[cat].unique())
                if vals:
                    filtered = filtered[filtered[cat].isin(vals)]

        st.dataframe(filtered.head())

        if chart=="Scatter":
            st.plotly_chart(px.scatter(filtered,x=x,y=y))
        elif chart=="Line":
            st.plotly_chart(px.line(filtered,x=x,y=y))
        elif chart=="Bar":
            st.plotly_chart(px.bar(filtered,x=x,y=y))
        else:
            st.plotly_chart(px.histogram(filtered,x=x))

# ---------- AI ----------
with tab3:
    st.subheader("🧠 AI Business Intelligence Engine")

    st.markdown("### 🔍 Select Analysis Type")

    analysis_type = st.selectbox(
        "Choose Insight Type",
        [
            "Full Business Analysis",
            "Growth Strategy",
            "Risk & Loophole Detection",
            "Profit Optimization",
            "Market Opportunities"
        ]
    )

    st.markdown("---")

    detail_level = st.selectbox(
        "Detail Level",
        ["Basic", "Detailed", "Advanced (Consultant Level)"]
    )

    st.markdown("---")

    if st.button("🚀 Generate AI Insights"):

        sample = data.head(15).to_string()

        prompt = f"""
        You are a senior business consultant.

        Analyze this dataset:
        {sample}

        Analysis Type: {analysis_type}
        Detail Level: {detail_level}

        Provide:
        1. Key Insights
        2. Growth Opportunities
        3. Risks & Loopholes
        4. Recommendations
        5. Strategic Plan
        """

        with st.spinner("Analyzing..."):
            output = safe_ai([{"role":"user","content":prompt}])
            st.success("Analysis Complete")
            st.write(output)

    # ---------- CHAT ----------
    with tab4:
        q = st.text_input("Ask")
        if q:
            st.write(safe_ai([{"role":"user","content":q}]))

# ---------- IDEAS ----------
with tab5:
    st.subheader("💡 AI Business Ideation Engine")

    # 🔹 Inputs
    industry = st.text_input("Industry (e.g., Retail, Healthcare, EdTech)")
    problem = st.text_area("Problem Statement (optional)")
    budget = st.selectbox("Budget Level", ["Low","Medium","High"])
    risk = st.selectbox("Risk Appetite", ["Low","Moderate","High"])

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    # 🚀 Startup Ideas
    if col1.button("🚀 Startup Ideas"):
        prompt = f"""
        Suggest 5 innovative startup ideas in {industry} industry.
        Budget: {budget}, Risk: {risk}.
        Problem: {problem}

        Provide:
        - Idea Name
        - Description
        - Revenue Model
        - Target Customers
        """
        with st.spinner("Generating ideas..."):
            out = safe_ai([{"role":"user","content":prompt}])
            st.success(out)
            save_history("Startup Ideas", out)

    # 📈 Growth Ideas
    if col2.button("📈 Growth Strategies"):
        prompt = f"""
        Suggest growth strategies for {industry}.
        Budget: {budget}.
        Include marketing, scaling, and digital expansion.
        """
        with st.spinner("Analyzing..."):
            out = safe_ai([{"role":"user","content":prompt}])
            st.success(out)
            save_history("Growth Ideas", out)

    # 💰 Cost Optimization
    if col3.button("💰 Cost Optimization"):
        prompt = f"""
        Suggest cost reduction strategies in {industry}.
        Focus on improving efficiency and profitability.
        """
        with st.spinner("Optimizing..."):
            out = safe_ai([{"role":"user","content":prompt}])
            st.success(out)
            save_history("Cost Ideas", out)

    st.markdown("---")

    # 📊 Business Plan
    if st.button("📊 Generate Business Plan"):
        prompt = f"""
        Create a structured business plan for {industry}.
        Budget: {budget}, Risk: {risk}.
        Problem: {problem}

        Include:
        - Executive Summary
        - Market Analysis
        - Revenue Model
        - Cost Structure
        - Growth Strategy
        """
        with st.spinner("Building plan..."):
            out = safe_ai([{"role":"user","content":prompt}])
            st.success(out)
            save_history("Business Plan", out)

    st.markdown("---")

    # 🤖 Data-Based Ideas (MOST POWERFUL 🔥)
    if st.button("🤖 Ideas from Uploaded Data"):
        sample = data.head(10).to_string()

        prompt = f"""
        Analyze this dataset:
        {sample}

        Provide:
        - Key insights
        - Business opportunities
        - Monetization strategies
        """
        with st.spinner("Analyzing dataset..."):
            out = safe_ai([{"role":"user","content":prompt}])
            st.success(out)
            save_history("Data Ideas", out)
   # ---------- PROFIT ----------
with tab6:
    st.subheader("💰 Profit Analytics Dashboard")

    # 🔹 Inputs
    revenue = st.number_input("Revenue (₹)", min_value=0.0)
    cost = st.number_input("Cost (₹)", min_value=0.0)

    # 🔹 Profit Calculation
    profit = revenue - cost

    col1, col2, col3 = st.columns(3)
    col1.metric("Revenue", f"₹{revenue}")
    col2.metric("Cost", f"₹{cost}")
    col3.metric("Profit", f"₹{profit}")

    # 🔹 Profit Margin
    if revenue > 0:
        margin = (profit / revenue) * 100
        st.metric("Profit Margin %", f"{round(margin,2)}%")

    st.markdown("---")

    # 🔹 Break-even Analysis
    st.subheader("📊 Break-even Analysis")

    fixed_cost = st.number_input("Fixed Cost (₹)", min_value=0.0)
    price = st.number_input("Selling Price per Unit (₹)", min_value=0.0)
    var_cost = st.number_input("Variable Cost per Unit (₹)", min_value=0.0)

    if price > var_cost:
        breakeven = fixed_cost / (price - var_cost)
        st.success(f"Break-even Units: {round(breakeven,2)}")
    else:
        st.warning("Price must be greater than Variable Cost")

    st.markdown("---")

    # 🔹 Profit Trend Simulation
    st.subheader("📈 Profit Simulation")

    units = st.slider("Units Sold", 1, 1000, 100)

    profit_list = []
    for u in range(1, units+1):
        p = (price - var_cost) * u - fixed_cost
        profit_list.append(p)

    st.line_chart(profit_list)

    st.markdown("---")

    # 🔹 AI Profit Suggestions
    if st.button("🤖 Improve Profit Strategy"):
        prompt = f"""
        Revenue: {revenue}
        Cost: {cost}
        Profit: {profit}

        Suggest ways to improve profitability, reduce cost, and increase revenue.
        """
        with st.spinner("Analyzing..."):
            output = safe_ai([{"role":"user","content":prompt}])
            st.success(output)
            save_history("Profit Strategy", output)
# ---------- FORECAST ----------
with tab7:
    st.subheader("📈 Advanced Forecasting (1–10 Years)")

    # 🔹 Select Column
    col = st.selectbox("Select Column for Forecast", data.select_dtypes(include=['int64','float64']).columns)

    values = data[col].dropna().values

    if len(values) > 3:

        # 🔹 Forecast Horizon
        years = st.slider("Select Forecast Period (Years)", 1, 10, 3)

        # 🔹 Convert years → steps
        steps = years  # assuming yearly data (you can later improve)

        # 🔹 Train Model
        X = np.arange(len(values)).reshape(-1,1)
        model = LinearRegression().fit(X, values)

        # 🔹 Future Prediction
        future_X = np.arange(len(values), len(values) + steps).reshape(-1,1)
        predictions = model.predict(future_X)

        # 🔹 Combine Data
        full_series = np.concatenate([values, predictions])

        # 🔹 Metrics
        st.metric("Last Actual Value", round(values[-1],2))
        st.metric("Final Forecast Value", round(predictions[-1],2))

        growth = ((predictions[-1] - values[-1]) / values[-1]) * 100 if values[-1] != 0 else 0
        st.metric("Forecast Growth %", f"{round(growth,2)}%")

        st.markdown("---")

        # 🔹 Visualization
        st.subheader("📊 Forecast Trend")

        st.line_chart(full_series)

        # 🔹 Table View
        st.subheader("📋 Forecast Data")

        forecast_df = pd.DataFrame({
            "Period": list(range(1, len(full_series)+1)),
            "Values": full_series
        })

        st.dataframe(forecast_df)

        st.markdown("---")

        # 🔹 AI Insight (VERY POWERFUL 🔥)
        if st.button("🤖 Explain Forecast"):
            prompt = f"""
            Current last value: {values[-1]}
            Forecast after {years} years: {predictions[-1]}

            Explain:
            - Trend
            - Growth pattern
            - Business meaning
            """
            with st.spinner("Analyzing trend..."):
                output = safe_ai([{"role":"user","content":prompt}])
                st.success(output)
                save_history("Forecast Insight", output)

    else:
        st.warning("Need at least 4 data points for forecasting")
# ---------- BUDGET ----------
with tab8:
    st.subheader("💰 Advanced Budget Planning Dashboard")

    # 🔹 Income & Expenses
    income = st.number_input("Monthly Income (₹)", min_value=0.0)
    expense = st.number_input("Monthly Expenses (₹)", min_value=0.0)

    savings = income - expense

    col1, col2, col3 = st.columns(3)
    col1.metric("Income", f"₹{income}")
    col2.metric("Expenses", f"₹{expense}")
    col3.metric("Savings", f"₹{savings}")

    # 🔹 Savings Rate
    if income > 0:
        savings_rate = (savings / income) * 100
        st.metric("Savings Rate %", f"{round(savings_rate,2)}%")

    st.markdown("---")

    # 🔹 Expense Breakdown
    st.subheader("📊 Expense Breakdown")

    food = st.number_input("Food", min_value=0.0)
    rent = st.number_input("Rent", min_value=0.0)
    travel = st.number_input("Travel", min_value=0.0)
    others = st.number_input("Others", min_value=0.0)

    expense_data = {
        "Food": food,
        "Rent": rent,
        "Travel": travel,
        "Others": others
    }

    exp_df = pd.DataFrame({
        "Category": list(expense_data.keys()),
        "Amount": list(expense_data.values())
    })

    st.plotly_chart(px.pie(exp_df, names="Category", values="Amount"))

    st.markdown("---")

    # 🔹 Budget vs Actual
    st.subheader("📉 Budget vs Actual")

    budget_limit = st.number_input("Set Monthly Budget (₹)", min_value=0.0)

    if budget_limit > 0:
        if expense > budget_limit:
            st.error("⚠️ You are over budget!")
        else:
            st.success("✅ Within budget")

    st.markdown("---")

    # 🔹 Savings Projection
    st.subheader("📈 Savings Projection")

    months = st.slider("Projection Period (Months)", 1, 60, 12)

    savings_trend = [savings * m for m in range(1, months+1)]

    st.line_chart(savings_trend)

    st.markdown("---")

    # 🔹 Goal Planning
    st.subheader("🎯 Financial Goal Planning")

    goal = st.number_input("Target Savings Goal (₹)", min_value=0.0)

    if savings > 0:
        months_needed = goal / savings if savings != 0 else 0
        st.info(f"Estimated Months to Reach Goal: {round(months_needed,1)}")

    st.markdown("---")

    # 🔹 AI Budget Advice
    if st.button("🤖 Get Budget Advice"):
        prompt = f"""
        Income: {income}
        Expenses: {expense}
        Savings: {savings}

        Suggest:
        - Budget improvement tips
        - Saving strategies
        - Expense optimization
        """
        with st.spinner("Analyzing..."):
            output = safe_ai([{"role":"user","content":prompt}])
            st.success(output)
            save_history("Budget Advice", output)

  # ---------- SUSTAINABILITY ----------
with tab9:
    st.subheader("🌱 Sustainability & ESG Dashboard")

    # 🔹 Inputs
    total_budget = st.number_input("Total Budget (₹)", min_value=0.0)
    green_investment = st.number_input("Green Investment (₹)", min_value=0.0)

    energy_usage = st.number_input("Energy Consumption (kWh)", min_value=0.0)
    carbon_emission = st.number_input("Carbon Emissions (kg CO₂)", min_value=0.0)

    st.markdown("---")

    # 🔹 ESG Metrics
    st.subheader("📊 ESG Metrics")

    if total_budget > 0:
        green_ratio = (green_investment / total_budget) * 100
    else:
        green_ratio = 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Green Investment %", f"{round(green_ratio,2)}%")
    col2.metric("Energy Usage", f"{energy_usage} kWh")
    col3.metric("Carbon Emissions", f"{carbon_emission} kg")

    st.markdown("---")

    # 🔹 Sustainability Score (Custom KPI)
    st.subheader("🌍 Sustainability Score")

    score = 100

    if green_ratio < 20:
        score -= 30
    if carbon_emission > 1000:
        score -= 30
    if energy_usage > 5000:
        score -= 20

    st.metric("Sustainability Score", f"{score}/100")

    if score > 80:
        st.success("Excellent Sustainability Performance 🌱")
    elif score > 50:
        st.warning("Moderate Sustainability ⚠️")
    else:
        st.error("Poor Sustainability ❌")

    st.markdown("---")

    # 🔹 Trend Simulation
    st.subheader("📈 Sustainability Improvement Projection")

    years = st.slider("Projection Years", 1, 10, 5)

    carbon_trend = [carbon_emission * (0.95 ** i) for i in range(years)]
    energy_trend = [energy_usage * (0.97 ** i) for i in range(years)]

    st.line_chart({
        "Carbon Emissions": carbon_trend,
        "Energy Usage": energy_trend
    })

    st.markdown("---")

    # 🔹 ESG Breakdown Chart
    st.subheader("📊 ESG Breakdown")

    esg_df = pd.DataFrame({
        "Category": ["Green Investment", "Carbon Impact", "Energy Use"],
        "Value": [green_investment, carbon_emission, energy_usage]
    })

    st.plotly_chart(px.bar(esg_df, x="Category", y="Value"))

    st.markdown("---")

    # 🔹 AI Sustainability Insights
    if st.button("🤖 Generate Sustainability Insights"):
        prompt = f"""
        Budget: {total_budget}
        Green Investment: {green_investment}
        Energy Usage: {energy_usage}
        Carbon Emissions: {carbon_emission}

        Provide:
        - Sustainability improvements
        - Cost-effective green strategies
        - ESG recommendations
        """
        with st.spinner("Analyzing sustainability..."):
            output = safe_ai([{"role":"user","content":prompt}])
            st.success(output)
            save_history("Sustainability Insights", output)

# ---------- COMPETITOR ----------
with tab10:
    st.subheader("📊 Advanced Competitor Analysis Dashboard")

    # 🔹 Inputs (FIX: added keys)
    your_rev = st.number_input("Your Revenue (₹)", min_value=0.0, key="comp_rev_you")
    comp_rev = st.number_input("Competitor Revenue (₹)", min_value=0.0, key="comp_rev_comp")

    your_cost = st.number_input("Your Cost (₹)", min_value=0.0, key="comp_cost_you")
    comp_cost = st.number_input("Competitor Cost (₹)", min_value=0.0, key="comp_cost_comp")

    st.markdown("---")

    # 🔹 Profit Comparison
    your_profit = your_rev - your_cost
    comp_profit = comp_rev - comp_cost

    col1, col2 = st.columns(2)
    col1.metric("Your Profit", f"₹{your_profit}")
    col2.metric("Competitor Profit", f"₹{comp_profit}")

    st.markdown("---")

    # 🔹 Market Share
    st.subheader("📊 Market Share Analysis")

    total_market = your_rev + comp_rev

    # FIX: default values to avoid crash
    your_share = 0
    comp_share = 0

    if total_market > 0:
        your_share = (your_rev / total_market) * 100
        comp_share = (comp_rev / total_market) * 100

        st.metric("Your Market Share %", f"{round(your_share,2)}%")
        st.metric("Competitor Market Share %", f"{round(comp_share,2)}%")

        pie_df = pd.DataFrame({
            "Company": ["You", "Competitor"],
            "Revenue": [your_rev, comp_rev]
        })

        st.plotly_chart(px.pie(pie_df, names="Company", values="Revenue"))

    else:
        st.info("Enter revenue values to see market share")

    st.markdown("---")

    # 🔹 Performance Comparison Chart
    st.subheader("📈 Performance Comparison")

    comp_df = pd.DataFrame({
        "Metric": ["Revenue", "Cost", "Profit"],
        "You": [your_rev, your_cost, your_profit],
        "Competitor": [comp_rev, comp_cost, comp_profit]
    })

    st.plotly_chart(px.bar(comp_df, x="Metric", y=["You","Competitor"], barmode="group"))

    st.markdown("---")

    # 🔹 Growth Simulation
    st.subheader("📈 Future Growth Simulation")

    # FIX: added keys
    years = st.slider("Projection Years", 1, 10, 5, key="comp_years")

    your_growth_rate = st.slider("Your Growth % per year", 0, 50, 10, key="comp_growth_you")
    comp_growth_rate = st.slider("Competitor Growth % per year", 0, 50, 8, key="comp_growth_comp")

    your_future = []
    comp_future = []

    y_val = your_rev
    c_val = comp_rev

    for i in range(years):
        y_val = y_val * (1 + your_growth_rate/100)
        c_val = c_val * (1 + comp_growth_rate/100)
        your_future.append(y_val)
        comp_future.append(c_val)

    st.line_chart({
        "Your Growth": your_future,
        "Competitor Growth": comp_future
    })

    st.markdown("---")

    # 🔹 Competitive Strength Score
    st.subheader("🏆 Competitive Strength Score")

    score = 50

    if your_profit > comp_profit:
        score += 20
    if your_share > comp_share:
        score += 20
    if your_growth_rate > comp_growth_rate:
        score += 10

    st.metric("Your Competitive Score", f"{score}/100")

    if score > 80:
        st.success("Strong Market Position 🚀")
    elif score > 50:
        st.warning("Moderate Competition ⚠️")
    else:
        st.error("High Competitive Risk ❌")

    st.markdown("---")

    # 🔹 AI Strategy Suggestions (FIX: key added)
    if st.button("🤖 Get Competitive Strategy", key="comp_ai_btn"):
        prompt = f"""
        My Revenue: {your_rev}
        Competitor Revenue: {comp_rev}
        My Profit: {your_profit}
        Competitor Profit: {comp_profit}

        Suggest:
        - How to outperform competitor
        - Pricing strategies
        - Growth strategies
        - Market positioning
        """
        with st.spinner("Analyzing competition..."):
            output = safe_ai([{"role":"user","content":prompt}])
            st.success(output)
            save_history("Competitor Strategy", output)

   # ---------- KPI ----------
with tab11:
    st.subheader("📊 Advanced KPI Dashboard")

    # 🔹 Select KPI Column
    kpi_col = st.selectbox(
        "Select KPI Column",
        data.select_dtypes(include=['int64','float64']).columns,
        key="kpi_col_select"
    )

    kpi_data = data[kpi_col].dropna().values

    if len(kpi_data) > 0:

        # 🔹 Metrics
        current = kpi_data[-1]
        avg = np.mean(kpi_data)

        growth = 0
        if len(kpi_data) > 1 and kpi_data[-2] != 0:
            growth = ((kpi_data[-1] - kpi_data[-2]) / kpi_data[-2]) * 100

        col1, col2, col3 = st.columns(3)
        col1.metric("Current Value", round(current,2))
        col2.metric("Average", round(avg,2))
        col3.metric("Growth %", f"{round(growth,2)}%")

        st.markdown("---")

        # 🔹 Trend Chart
        st.subheader("📈 KPI Trend")
        st.line_chart(kpi_data)

        st.markdown("---")

        # 🔹 Moving Average (NEW 🔥)
        st.subheader("📊 Moving Average Analysis")

        window = st.slider("Select Window Size", 2, 20, 5, key="kpi_window")

        if len(kpi_data) >= window:
            rolling_avg = pd.Series(kpi_data).rolling(window).mean()

            df_ma = pd.DataFrame({
                "Actual": kpi_data,
                "Moving Avg": rolling_avg
            })

            st.line_chart(df_ma)
        else:
            st.warning("Not enough data for selected window")

        st.markdown("---")

        # 🔹 Forecasting (Advanced 🔥)
        st.subheader("🔮 KPI Forecast")

        years = st.slider("Forecast Period", 1, 10, 3, key="kpi_forecast_years")

        if len(kpi_data) > 3:
            X = np.arange(len(kpi_data)).reshape(-1,1)
            model = LinearRegression().fit(X, kpi_data)

            future_X = np.arange(len(kpi_data), len(kpi_data)+years).reshape(-1,1)
            predictions = model.predict(future_X)

            full_series = np.concatenate([kpi_data, predictions])

            st.metric("Next Predicted Value", round(predictions[0],2))
            st.metric("Final Forecast Value", round(predictions[-1],2))

            st.line_chart(full_series)

            # Table view
            forecast_df = pd.DataFrame({
                "Period": list(range(1, len(full_series)+1)),
                "Value": full_series
            })

            st.dataframe(forecast_df)

        else:
            st.warning("Need at least 4 data points for forecasting")

        st.markdown("---")

        # 🔹 AI KPI Insights
        if st.button("🤖 Generate KPI Insights", key="kpi_ai_btn"):
            prompt = f"""
            KPI Data Summary:
            Current Value: {current}
            Average: {avg}
            Growth: {growth}

            Provide:
            - Trend explanation
            - Performance evaluation
            - Business recommendations
            """
            with st.spinner("Analyzing KPI..."):
                output = safe_ai([{"role":"user","content":prompt}])
                st.success(output)
                save_history("KPI Insights", output)

    else:
        st.warning("No KPI data available")
