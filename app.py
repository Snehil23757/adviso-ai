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
        if st.button("Generate Insights"):
            out = safe_ai([{"role":"user","content":data.head().to_string()}])
            st.write(out)

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
        b = st.number_input("Budget")
        g = st.number_input("Green")
        if st.button("Check"):
            st.write(safe_ai([{"role":"user","content":f"{b},{g}"}]))

    # ---------- COMPETITOR ----------
    with tab10:
        y = st.number_input("Your Revenue")
        c = st.number_input("Competitor")
        if st.button("Compare"):
            st.write(safe_ai([{"role":"user","content":f"{y} vs {c}"}]))

    # ---------- KPI ----------
    with tab11:
        col = st.selectbox("KPI", data.select_dtypes(include=['int64','float64']).columns)
        k = data[col].dropna().values

        if len(k)>0:
            st.metric("Current", k[-1])
            st.line_chart(k)

            if len(k)>3:
                m = LinearRegression().fit(np.arange(len(k)).reshape(-1,1), k)
                pred = m.predict([[len(k)]])[0]
                st.metric("Next", round(pred,2))
