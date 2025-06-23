#user_analysis.py
import pandas as pd
import streamlit as st
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

def show_user_logs(df, selected_user):
    user_logs = df[df["UserID"] == selected_user]

    # 👤 Kullanıcı Bilgileri
    user_info = user_logs.iloc[0] if not user_logs.empty else {}

    if "AccessLevel" in user_logs.columns:
        access_types = (
            user_logs["AccessLevel"]
            .dropna()
            .astype(str)
            .str.lower()
            .str.strip()
            .map(lambda x: x[0])  # ör: "read" → "r", "write" → "w"
            .dropna()
            .unique()
        )
        access_types_sorted = sorted(set(access_types))
        access_type_display = ", ".join(access_types_sorted)
    else:
        access_type_display = "bilinmiyor"

    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Kullanıcı ID", selected_user)
    with col2:
        st.metric("Rol", user_info.get("UserRole", "Bilinmiyor"))
    with col3:
        st.metric("Erişim Türleri", access_type_display)

    # 📊 Log Oranı
    user_log_count = len(user_logs)
    total_log_count = len(df)
    user_log_ratio = (user_log_count / total_log_count * 100) if total_log_count > 0 else 0

    # ⏱ Ortalama Süre Karşılaştırması
    if "AccessDuration" in df.columns:
        try:
            user_avg = user_logs["AccessDuration"].astype(float).mean()
            overall_avg = df["AccessDuration"].astype(float).mean()
            duration_ratio = f"{user_avg:.2f} / {overall_avg:.2f} sn"
        except:
            duration_ratio = "Hesaplanamadı"
    else:
        duration_ratio = "Veri yok"

    # 👉 Üçlü metrik kutusu
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📈 Kullanıcı Log Sayısı", f"{user_log_count}")
    with col2:
        st.metric("📊 Log Oranı (%)", f"{user_log_ratio:.2f}%")
    with col3:
        st.metric("⏱ Süre (Kullanıcı / Genel)", duration_ratio)

    return user_logs  # 🔧 HER DURUMDA DÖN!


def plot_user_hour_distribution(user_logs):
    if "Timestamp" not in user_logs.columns:
        st.warning("Timestamp kolonu yok.")
        return

    user_logs["Timestamp"] = pd.to_datetime(user_logs["Timestamp"], dayfirst=True, errors='coerce')
    user_logs["Hour"] = user_logs["Timestamp"].dt.hour

    fig = px.scatter(user_logs, x="Timestamp", y="Hour", title="🕒 Erişim Saatleri (Scatter)", 
                     labels={"Hour": "Saat"}, height=300)
    st.plotly_chart(fig, use_container_width=True)

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
