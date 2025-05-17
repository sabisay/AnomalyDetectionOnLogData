import streamlit as st
from data_loader import load_data
from dashboard import show_general_dashboard
from api_utils import post_preprocess_api
from visualization import (
    plot_access_duration_histogram,
    plot_user_access_bar,
    plot_time_series
)

st.set_page_config(page_title="Anomali Tespit Arayüzü", layout="wide")
st.title("📊 Anomali Tespit Uygulaması")


uploaded_file = st.file_uploader("Veri dosyasını yükleyin (.csv, .xlsx):", type=["csv", "xlsx"])

if uploaded_file:
    df, error = load_data(uploaded_file)
    if error:
        st.error(error)
    else:
        st.success("Veri başarıyla yüklendi ✅")
        

        # --- Yeni Dashboard ---
        show_general_dashboard(df)
        

        st.markdown("---")
        # Preprocessing ve model adımları, anomaly görselleri için visualization.py fonksiyonlarını sonra çağırabilirsin
        if st.button("🔎 Analize Başla (Preprocessing)"):
            with st.spinner("Veri işleniyor..."):
                processed_df, err = post_preprocess_api(df)
            if err:
                st.error(f"Preprocessing API hatası: {err}")
            else:
                st.success("Preprocessing başarılı!")
                st.dataframe(processed_df.head())
                # (Burada model/visualization fonksiyonlarını çağırırsın)

        st.subheader("🧾 Veri Önizleme")
        st.dataframe(df.head())
else:
    st.info("Lütfen bir veri dosyası yükleyin.")
