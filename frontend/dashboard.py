import streamlit as st
import pandas as pd
import plotly.express as px

def show_general_dashboard(df):
    st.subheader("📊 General Access Dashboard")

    # --- Top metrics ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Access Count", len(df))
    with col2:
        st.metric("Unique Users", df["UserID"].nunique())
    with col3:
        if "Timestamp" in df.columns:
            # HERE: dayfirst=True for Turkish style date parsing
            min_date = pd.to_datetime(df['Timestamp'], dayfirst=True).min().strftime("%d.%m.%Y")
            max_date = pd.to_datetime(df['Timestamp'], dayfirst=True).max().strftime("%d.%m.%Y")
            st.metric("Date Range", f"{min_date} - {max_date}")
        else:
            st.info("No Timestamp column")

    # --- Top 5 Users & 3-hour Access Count ---
    st.markdown(" ")
    col4, col5 = st.columns(2)
    with col4:
        if "UserID" in df.columns and "UserRole" in df.columns:
            top_users = df.groupby(['UserID', 'UserRole']).size().reset_index(name='Count')
            top_users = top_users.sort_values(by='Count', ascending=False).head(5)
            fig_top_users = px.bar(
            top_users, 
            x="UserID", 
            y="Count", 
            color="UserRole",
            title="Top 5 Users",
            height=300,
            color_discrete_map={
                "Nurse": "#4D96FF", 
                "Admin": "#FFB72B",
                "Doctor": "#8AC588",
                "Researcher": "#9662A2",
                "Secretary": "#C37322",
            },
            category_orders={"UserID": top_users["UserID"].tolist()}
)
            fig_top_users.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_top_users, use_container_width=True)
        else:
            st.info("Missing UserID or UserRole column")

    with col5:
        if "Timestamp" in df.columns:
            # *** USE dayfirst=True HERE AS WELL ***
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], dayfirst=True)
            df['3h_slot'] = df['Timestamp'].dt.floor('3H')
            slot_range = pd.date_range(
                start=df['3h_slot'].min().floor('D'),
                end=df['3h_slot'].max().ceil('D') - pd.Timedelta(hours=0),
                freq='3H'
            )
            count_3h = df.groupby('3h_slot').size().reindex(slot_range, fill_value=0).reset_index()
            count_3h.columns = ['3h_slot', 'Access_Count']
            fig_3h = px.line(
                count_3h, x='3h_slot', y='Access_Count',
                title="Access Count (Every 3 Hours, Complete Timeline)",
                height=300
            )
            fig_3h.update_layout(
                xaxis_title="Datetime (every 3 hours)",
                yaxis_title="Access Count",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_3h, use_container_width=True)
        else:
            st.info("No Timestamp column")

    # --- Access Level Bar + Avg Duration metric next to it + Sensitive Pie chart ---
    st.markdown(" ")
    col6, col7, col8 = st.columns([3, 1, 2])
    with col6:
        if "AccessDuration" in df.columns and "AccessLevel" in df.columns:
            duration_by_level = df.groupby("AccessLevel")["AccessDuration"].agg(['count', 'mean']).reset_index()
            fig_duration = px.bar(
                duration_by_level, x="AccessLevel", y="mean",
                title="Average Access Duration per Access Level",
                labels={'mean': 'Average Duration (s)'},
                height=300
            )
            fig_duration.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_duration, use_container_width=True)
        else:
            st.info("Missing AccessDuration or AccessLevel column")

    with col7:
        if "AccessDuration" in df.columns:
            st.metric("Avg. Access Duration (ms)", f"{df['AccessDuration'].mean():.1f}")

    with col8:
        if "IsSensitive" in df.columns:
            sensitive_counts = df["IsSensitive"].value_counts().reset_index()
            sensitive_counts.columns = ["IsSensitive", "Count"]
            fig_sensitive = px.pie(
                sensitive_counts, values="Count", names="IsSensitive",
                title="Sensitive Access Analysis",
                height=300
            )
            fig_sensitive.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_sensitive, use_container_width=True)
        else:
            st.info("No IsSensitive column")
