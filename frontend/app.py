import os
import streamlit as st
import pandas as pd
import requests
from data_loader import load_data, save_and_forward
from dashboard import show_general_dashboard
from user_analysis import (
    show_user_logs,
    plot_user_hour_distribution,
    plot_access_level_distribution,
    plot_department_distribution,
    show_sensitive_accesses
)


import jwt
import time

st.set_page_config(page_title="Hasta Verilerine Erişimde Anomali Tespiti", layout="wide")

API_URL = "http://localhost:5000"

def render_navbar(user_info):
    col1, col2, col3 = st.columns([5, 1, 1])
    
    with col1:
        st.markdown(f"👤 **{user_info['username']}** ({user_info['role']})")

    with col2:
        if st.session_state.page == "results":
            if st.button("⏪ Yeni Tespit"):
                st.session_state.page = "upload"
                st.session_state.df = None
                st.session_state.abnormals = []
                st.session_state.selected_user = None
                st.session_state.show_user_analysis = False
                st.rerun()

    with col3:
        if st.button("🚪 Çıkış Yap"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# --- Sayfa yönetimi
if "page" not in st.session_state:
    st.session_state.page = "upload"
if "df" not in st.session_state:
    st.session_state.df = None
if "abnormals" not in st.session_state:
    st.session_state.abnormals = []
if "selected_user" not in st.session_state:
    st.session_state.selected_user = None

# --- Kimlik kontrolü
if "token" not in st.session_state:
    st.session_state.token = None

user_info = None
if st.session_state.token:
    try:
        user_info = jwt.decode(st.session_state.token, options={"verify_signature": False})
    except Exception:
        st.session_state.token = None
        st.warning("Geçersiz token.")

if not st.session_state.token:
    with st.form("login_form"):
        st.subheader("🔐 Giriş Yap")
        username = st.text_input("Kullanıcı adı")
        password = st.text_input("Şifre", type="password")
        submitted = st.form_submit_button("Giriş")

        if submitted:
            res = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
            if res.status_code == 200:
                st.session_state.token = res.json()["token"]
                st.success("Giriş başarılı, yönlendiriliyorsunuz...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Giriş başarısız.")

# --- Sayfa: Veri Yükleme ve Tespit

elif st.session_state.page == "upload" and user_info:
    render_navbar(user_info)
    st.title("📥 Veri Yükleme & Anomali Tespiti")
    uploaded_file = st.file_uploader("Verinizi yükleyin:", type=["csv", "xlsx"])

    if uploaded_file:
        df, error = load_data(uploaded_file)
        if error:
            st.error(error)
        else:
            st.success("Veri başarıyla yüklendi ✅")
            show_general_dashboard(df)

            for ext in [".csv", ".xlsx"]:
                temp_path = os.path.abspath(f"temp_uploaded{ext}")
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception as e:
                        print(f"[Silme Hatası] {temp_path} silinemedi: {e}")

            file_path, _, error = save_and_forward(uploaded_file)
            if error:
                st.error(error)
            else:
                if user_info["role"] in ["admin", "analyst"]:    
                    if st.button("🚀 Anomali Tespitini Başlat"):
                        headers = {"Authorization": f"Bearer {st.session_state.token}"}
                        with st.spinner("Model çalıştırılıyor..."):
                            res = requests.post(f"{API_URL}/run-detection", files={"file": uploaded_file}, headers=headers)
                        if res.status_code == 200:
                            result = res.json()
                            st.session_state.abnormals = result["abnormal_users"]
                            st.session_state.df = df
                            st.session_state.selected_user = st.session_state.abnormals[0]
                            st.session_state.page = "results"
                            st.rerun()
                        else:
                            st.error(f"❌ Hata: {res.text}")


# --- Sayfa: Sonuçlar ve Analiz
elif st.session_state.page == "results" and user_info:
    render_navbar(user_info)
    st.title("🔎 Anomali Tespiti Sonuçları")
    st.info("Model çalışması tamamlandı. Aşağıda sonuçlar yer almakta.")

    # Role: admin => detaylı analiz
    if user_info["role"] == "admin":
        st.success("Gelişmiş analiz modu (Admin)")

        st.markdown(f"### 👥 Toplam {len(st.session_state.abnormals)} anormal kullanıcı tespit edildi.")
        st.dataframe(pd.DataFrame(st.session_state.abnormals, columns=["Anormal Kullanıcılar"]))

        st.markdown(f"📌 İncelenen kullanıcı: `{st.session_state.selected_user}`")
        selected = st.selectbox("Başka bir kullanıcı seçin:", st.session_state.abnormals,
                                index=st.session_state.abnormals.index(st.session_state.selected_user))
        st.session_state.selected_user = selected

        if st.session_state.df is not None:
            user_logs = show_user_logs(st.session_state.df, selected)
            plot_user_hour_distribution(user_logs)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📊 Eriişim Türü Dağılımı")
                plot_access_level_distribution(user_logs)
            with col2:
                st.markdown("### 🏢 Departman Dağılımı")
                plot_department_distribution(user_logs)
            show_sensitive_accesses(user_logs)

            st.markdown("---")
            st.subheader("📄 Kullanıcının Tüm Logları (Detaylı)")
            st.dataframe(user_logs)

    # Role: analyst => sadece liste
    elif user_info["role"] == "analyst":
        st.warning("Bu sayfa yalnızca kullanıcı listesini gösterir (Analyst)")
        st.markdown(f"👥 Toplam {len(st.session_state.abnormals)} anormal kullanıcı tespit edildi.")
        st.table(pd.DataFrame(st.session_state.abnormals, columns=["Anormal Kullanıcılar"]))


    # Role bilinmiyorsa
    else:
        st.error("Bu sayfa yalnızca admin ve analyst rollerine özeldir.")

