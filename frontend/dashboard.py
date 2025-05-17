import streamlit as st
import pandas as pd
import plotly.express as px

def show_general_dashboard(df):
    st.subheader("📊 Genel Erişim Dashboard'u")

    # METRICS (yan yana)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Toplam Erişim", len(df))

    with col2:
        if "User_ID" in df.columns:
            st.metric("Farklı Kullanıcı", df["User_ID"].nunique())
        else:
            st.info("User_ID yok")

    with col3:
        if "Access_Duration" in df.columns:
            st.metric("Ortalama Erişim Süresi", f"{df['Access_Duration'].mean():.2f}")
        else:
            st.info("Access_Duration yok")

    # EN ÇOK ERİŞİM YAPANLAR ve Roller - 2 küçük grafik yanyana
    st.markdown(" ")
    col4, col5 = st.columns(2)

    with col4:
        if "User_ID" in df.columns:
            user_counts = df["User_ID"].value_counts().reset_index()
            user_counts.columns = ["User_ID", "Access_Count"]
            fig_users = px.bar(
                user_counts.head(5),
                x="User_ID", y="Access_Count",
                title="En Çok Erişim Yapan 5 Kullanıcı",
                height=300
            )
            st.plotly_chart(fig_users, use_container_width=True)

    with col5:
        if "User_Role" in df.columns:
            role_counts = df["User_Role"].value_counts().reset_index()
            role_counts.columns = ["User_Role", "Count"]
            fig_roles = px.bar(
                role_counts, 
                x="User_Role", y="Count",
                title="Kullanıcı Rolleri Dağılımı",
                height=300
            )
            st.plotly_chart(fig_roles, use_container_width=True)

    # Access Level Pasta Grafiği
    st.markdown(" ")
    if "Access_Level" in df.columns:
        col6, _ = st.columns([2,1])
        access_level_counts = df["Access_Level"].value_counts().reset_index()
        access_level_counts.columns = ["Access_Level", "Count"]
        fig_access = px.pie(
            access_level_counts, 
            values="Count", 
            names="Access_Level", 
            title="Access Level Dağılımı",
            height=250
        )
        with col6:
            st.plotly_chart(fig_access, use_container_width=True)
