import streamlit as st
import pandas as pd

# Clear fields flag logic (runs BEFORE widgets)
if st.session_state.get("clear_fields_flag", False):
    st.session_state["names_input"] = ""
    st.session_state["order_input"] = ""
    st.session_state["clear_fields_flag"] = False

# Session state for persistent data across reruns
if "data" not in st.session_state:
    st.session_state.data = {}
    st.session_state.display_names = {}
    st.session_state.groups = []
    st.session_state.FOOD = {}

st.title("Order Splitter")

with st.form("order_form"):
    names_input = st.text_input("Enter name(s) (comma-separated):", key="names_input")
    order_input = st.text_input("Enter order (dish price, e.g. 'squash 12.99, gingersushi 4.99'):", key="order_input")
    submitted = st.form_submit_button("Add Order")
    
    if submitted and names_input and order_input:
        names_raw = [name.strip() for name in names_input.split(",") if name.strip()]
        names = [name.lower() for name in names_raw]
        for i in range(len(names)):
            if names[i] not in st.session_state.display_names:
                st.session_state.display_names[names[i]] = names_raw[i]
        items = [item.strip() for item in order_input.split(",")]
        total_cost = 0.0
        for item in items:
            try:
                parts = item.rsplit(" ", 1)
                dish = parts[0].lower()
                price = float(parts[1])
                total_cost += price
                if dish not in st.session_state.FOOD:
                    st.session_state.FOOD[dish] = price
            except (IndexError, ValueError):
                st.warning(f"Invalid item format: '{item}' — skipping")
        if names:
            split_cost = total_cost / len(names)
            for name in names:
                if name in st.session_state.data:
                    st.session_state.data[name] += split_cost
                else:
                    st.session_state.data[name] = split_cost
            st.session_state.groups.append(names)

# ---- CLEAR FIELDS BUTTON (OUTSIDE FORM) ----
if st.button("Clear Fields"):
    st.session_state["clear_fields_flag"] = True
    st.experimental_rerun() if hasattr(st, "experimental_rerun") else st.rerun()

# Build table
already_displayed = set()
table_rows = []
for group in st.session_state.groups:
    for name in group:
        if name not in already_displayed:
            table_rows.append({
                "Name": st.session_state.display_names[name],
                "Total Cost": round(st.session_state.data[name], 2)
            })
            already_displayed.add(name)
    table_rows.append({"Name": "", "Total Cost": ""})

# Remove last blank row if any
if table_rows and table_rows[-1] == {"Name": "", "Total Cost": ""}:
    table_rows.pop()

df = pd.DataFrame(table_rows)
st.dataframe(df)
st.download_button("Download as CSV", df.to_csv(index=False), "orders_summary.csv")

if st.session_state.FOOD:
    st.write("All dishes entered:")
    st.json(st.session_state.FOOD)
