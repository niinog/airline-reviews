import streamlit as st
import requests
import pandas as pd
import altair as alt

st.set_page_config(page_title="Airline Review Analyzer", layout="centered")

st.title("✈️ Airline Customer Review Analyzer")
st.markdown("Select an airline to understand what passengers talk about the most.")

# Predefined airline options (you can expand this)
airlines = [
    "Wizzair", "Ryanair", "Turkish Airlines", "EasyJet", "Delta",
    "Qatar Airways", "United", "Lufthansa", "Air France", "British Airways"
]

selected_airline = st.selectbox("Choose an airline", sorted(airlines))
post_limit = st.slider("Number of Reddit posts to analyze", min_value=10, max_value=300, step=10, value=100)

if st.button("Analyze Topics"):
    with st.spinner("Fetching and analyzing Reddit posts..."):
        api_url = f"http://127.0.0.1:8000/get_posts?airline={selected_airline}&total_limit={post_limit}"

        
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            summary = data["category_summary"]
            df_summary = pd.DataFrame(summary)

            if df_summary.empty:
                st.warning("No posts found for this airline.")
            else:
                st.subheader(f"📊 What people talk about for {selected_airline}")

                chart = alt.Chart(df_summary).mark_bar().encode(
                    x=alt.X("topic_label", sort='-y', title="Category"),
                    y=alt.Y("count", title="Number of Posts"),
                    tooltip=["topic_label", "count"]
                ).properties(width=700, height=400)
                st.altair_chart(chart)

                st.subheader("📝 Sample Complaints by Category")
                for row in summary:
                    with st.expander(f"{row['topic_label']} ({row['count']} posts)"):
                        st.write(f"🔗 [Read full post]({row['example']['url']})")
                        st.write(f"**Title:** {row['example']['title']}")
                        st.write(row['example']['text'])

        else:
            st.error("🚨 Failed to retrieve data. Is your FastAPI running?")
