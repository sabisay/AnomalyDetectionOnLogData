#user_analysis.py
import pandas as pd
import streamlit as st
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt


def show_user_logs(df, selected_user):
    user_logs = df[df["UserID"] == selected_user]

    # 👤 Kullanıcı Bilgileri
    st.subheader(f"👤 {selected_user} - Kullanıcı Bilgileri")
    user_info = user_logs.iloc[0] if not user_logs.empty else {}
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("User ID", selected_user)
    with col2:
        st.metric("Role", user_info.get("Role", "Bilinmiyor"))
    with col3:
        st.metric("Department", user_info.get("Department", "Bilinmiyor"))

    # 📊 Log Oranı
    user_log_count = len(user_logs)
    total_log_count = len(df)
    user_log_ratio = (user_log_count / total_log_count * 100) if total_log_count > 0 else 0
    st.metric("📈 Kullanıcı Log Oranı", f"{user_log_count} / {total_log_count} ({user_log_ratio:.2f}%)")

    # ⏱ Ortalama Süre Karşılaştırması
    if "AccessDuration" in df.columns:
        try:
            user_avg = user_logs["AccessDuration"].astype(float).mean()
            overall_avg = df["AccessDuration"].astype(float).mean()
            st.metric("Ortalama Süre (Kullanıcı)", f"{user_avg:.2f} sn")
            st.metric("Ortalama Süre (Genel)", f"{overall_avg:.2f} sn")
        except:
            st.warning("AccessDuration sütunu sayı değil, ortalama hesaplanamadı.")

    return user_logs


def plot_user_access_timeline(user_logs):
    if "Timestamp" not in user_logs.columns:
        st.warning("Timestamp kolonu yok.")
        return

    user_logs["Timestamp"] = pd.to_datetime(user_logs["Timestamp"], dayfirst=True, errors='coerce')
    user_logs["AccessDate"] = user_logs["Timestamp"].dt.date

    access_counts = user_logs.groupby("AccessDate").size().reset_index(name="Access Count")

    fig = px.line(access_counts, x="AccessDate", y="Access Count", title="📆 Günlük Erişim Grafiği")
    st.plotly_chart(fig, use_container_width=True)


def plot_user_hour_distribution(user_logs):
    if "Timestamp" not in user_logs.columns:
        st.warning("Timestamp kolonu yok.")
        return

    user_logs["Timestamp"] = pd.to_datetime(user_logs["Timestamp"], dayfirst=True, errors='coerce')
    user_logs["Hour"] = user_logs["Timestamp"].dt.hour

    fig = px.scatter(user_logs, x="Timestamp", y="Hour", title="🕒 Erişim Saatleri (Scatter)", 
                     labels={"Hour": "Saat"}, height=300)
    st.plotly_chart(fig, use_container_width=True)


def plot_user_temporal_heatmap(user_logs):
    if "Timestamp" not in user_logs.columns:
        st.warning("Timestamp kolonu yok.")
        return

    user_logs["Timestamp"] = pd.to_datetime(user_logs["Timestamp"], dayfirst=True, errors='coerce')
    user_logs["Date"] = user_logs["Timestamp"].dt.date
    user_logs["Hour"] = user_logs["Timestamp"].dt.hour

    pivot = user_logs.groupby(["Date", "Hour"]).size().reset_index(name="AccessCount")
    pivot_pivoted = pivot.pivot(index="Date", columns="Hour", values="AccessCount").fillna(0)

    fig, ax = plt.subplots(figsize=(12, max(3, len(pivot_pivoted) * 0.3)))
    sns.heatmap(pivot_pivoted, cmap="YlGnBu", linewidths=0.1, cbar_kws={"label": "Erişim Sayısı"})
    ax.set_title("🗓️ Tarih-Saat Bazlı Erişim Yoğunluğu")
    ax.set_xlabel("Saat")
    ax.set_ylabel("Tarih")
    st.pyplot(fig)


def show_sensitive_accesses(user_logs):
    if "IsSensitive" not in user_logs.columns:
        st.info("Bu veride 'IsSensitive' kolonu yok.")
        return

    sensitive_logs = user_logs[user_logs["IsSensitive"] == True]
    sensitive_count = len(sensitive_logs)

    st.metric("🔒 Sensitive Erişim Sayısı", sensitive_count)
    if sensitive_count > 0:
        st.markdown("**📌 Sensitive Erişim Log ID'leri:**")
        st.write(sensitive_logs["LogID"].tolist() if "LogID" in sensitive_logs.columns else sensitive_logs.index.tolist())
