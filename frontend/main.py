import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Başlık ve açıklama
st.set_page_config(page_title="Anomali Tespit Arayüzü", layout="wide")
st.title("📊 Anomali Tespit Uygulaması")
st.markdown("Bu uygulama ile veri yükleyebilir, önizleyebilir ve grafiklerle keşifsel analiz yapabilirsiniz.")

# Veri yükleme
uploaded_file = st.file_uploader("Veri dosyasını yükleyin (.csv, .xlsx):", type=["csv", "xlsx"])

# Yüklenen dosya varsa oku ve göster
if uploaded_file:
    # Uygun dosya türüne göre oku
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("🧾 Veri Önizleme")
    st.dataframe(df.head())

    # Sayısal sütunları seç
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if numeric_cols:
        st.subheader("📈 Sayısal Özelliklerin İstatistikleri")
        st.write(df[numeric_cols].describe())

        # Grafik çizimi için sütun seçimi
        st.subheader("📉 Grafiksel İnceleme")
        selected_col = st.selectbox("Bir sütun seçin (zaman serisi/dağılım)", numeric_cols)

        # Matplotlib ile çizim
        fig, ax = plt.subplots()
        ax.plot(df[selected_col])
        ax.set_title(f"{selected_col} Zaman Serisi")
        ax.set_xlabel("Kayıt")
        ax.set_ylabel(selected_col)
        st.pyplot(fig)

        # Plotly ile dağılım
        st.subheader("📍 Plotly ile Dağılım Grafiği")
        fig2 = px.histogram(df, x=selected_col)
        st.plotly_chart(fig2)

    else:
        st.warning("Sayısal sütun bulunamadı, grafik çizilemiyor.")
else:
    st.info("Lütfen bir veri dosyası yükleyin.")

