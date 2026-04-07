# ---------- CHARTS ----------
with tab2:
    st.subheader("📈 Smart Charts with Filters")

    chart = st.selectbox("Chart Type", ["Scatter","Line","Bar","Histogram","Box","Pie"])

    # 🔹 Column Selection
    x = st.selectbox("X Axis", data.columns)
    y = st.selectbox("Y Axis", data.select_dtypes(include=['int64','float64']).columns)

    filtered_data = data.copy()

    # 🔹 CATEGORY FILTER
    st.subheader("🔍 Filters")

    cat_cols = data.select_dtypes(include=['object']).columns.tolist()

    if len(cat_cols) > 0:
        cat_filter = st.selectbox("Filter by Category Column (optional)", ["None"] + cat_cols)

        if cat_filter != "None":
            unique_vals = data[cat_filter].dropna().unique()
            selected_vals = st.multiselect("Select Values", unique_vals)

            if selected_vals:
                filtered_data = filtered_data[filtered_data[cat_filter].isin(selected_vals)]

    # 🔹 NUMERIC RANGE FILTER
    num_cols = data.select_dtypes(include=['int64','float64']).columns.tolist()

    if len(num_cols) > 0:
        range_col = st.selectbox("Filter by Numeric Range (optional)", ["None"] + num_cols)

        if range_col != "None":
            min_val = float(data[range_col].min())
            max_val = float(data[range_col].max())

            selected_range = st.slider("Select Range", min_val, max_val, (min_val, max_val))

            filtered_data = filtered_data[
                (filtered_data[range_col] >= selected_range[0]) &
                (filtered_data[range_col] <= selected_range[1])
            ]

    # 🔹 SORTING
    st.subheader("↕️ Sorting")

    sort_col = st.selectbox("Sort by Column", ["None"] + list(filtered_data.columns))
    order = st.radio("Order", ["Ascending","Descending"])

    if sort_col != "None":
        filtered_data = filtered_data.sort_values(
            by=sort_col,
            ascending=True if order == "Ascending" else False
        )

    # 🔹 PREVIEW FILTERED DATA
    st.subheader("📊 Filtered Data Preview")
    st.dataframe(filtered_data.head(20))

    # 🔹 CHARTS
    st.subheader("📉 Visualization")

    if len(filtered_data) > 0:
        if chart == "Scatter":
            st.plotly_chart(px.scatter(filtered_data, x=x, y=y))
        elif chart == "Line":
            st.plotly_chart(px.line(filtered_data, x=x, y=y))
        elif chart == "Bar":
            st.plotly_chart(px.bar(filtered_data, x=x, y=y))
        elif chart == "Histogram":
            st.plotly_chart(px.histogram(filtered_data, x=x))
        elif chart == "Box":
            st.plotly_chart(px.box(filtered_data, x=x, y=y))
        elif chart == "Pie":
            st.plotly_chart(px.pie(filtered_data, names=x, values=y))
    else:
        st.warning("No data available after applying filters")
