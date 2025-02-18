import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static
import gspread
from google.oauth2 import service_account

# Configurar credenciales de Google
def cargar_credenciales():
    creds = service_account.Credentials.from_service_account_file(
        "credentials.json",
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"],
    )
    return creds

# Conectar con Google Sheets
def conectar_google_sheets():
    creds = cargar_credenciales()
    client = gspread.authorize(creds)
    sheet = client.open("Mactor_FAST_Turismo").sheet1
    return sheet

# Cargar datos desde Google Sheets
def cargar_datos():
    sheet = conectar_google_sheets()
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Guardar datos en Google Sheets
def guardar_datos(df):
    sheet = conectar_google_sheets()
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

# UI/UX Mejorada con navegación
st.sidebar.title("Menú de Navegación")
opcion = st.sidebar.radio("Seleccione una opción", ["Ingreso de Datos", "Visualización de Datos", "Mapa Interactivo"])

# Cargar o inicializar datos
try:
    df = cargar_datos()
except:
    df = pd.DataFrame(columns=["Actor", "Objetivo", "Influencia", "Tipo", "Latitud", "Longitud"])

if opcion == "Ingreso de Datos":
    st.title("Ingreso de Datos - MACTOR y FAST")
    with st.form("formulario_datos"):
        actor = st.text_input("Nombre del Actor")
        objetivo = st.text_input("Objetivo Estratégico")
        influencia = st.slider("Nivel de Influencia", -1, 1, 0)
        tipo = st.selectbox("Clasificación (FAST)", ["Factor", "Atractor", "Sistema de Soporte"])
        latitud = st.number_input("Latitud", format="%.6f")
        longitud = st.number_input("Longitud", format="%.6f")
        submit = st.form_submit_button("Agregar Datos")

        if submit and actor and objetivo:
            nuevo_dato = pd.DataFrame([[actor, objetivo, influencia, tipo, latitud, longitud]], columns=df.columns)
            df = pd.concat([df, nuevo_dato], ignore_index=True)
            guardar_datos(df)
            st.success("Datos guardados correctamente")

if opcion == "Visualización de Datos":
    st.title("Análisis de Relaciones de Poder y Conflicto")
    st.dataframe(df)

    if not df.empty:
        st.subheader("Gráfico de Influencia de Actores")

        fig = px.bar(df, x="Actor", y="Influencia", color="Objetivo", barmode="group", title="Influencia de Actores por Objetivo")
        st.plotly_chart(fig)

        fig2 = px.scatter(df, x="Actor", y="Influencia", color="Tipo", size_max=10, title="Mapa de Posicionamiento de Actores según FAST")
        st.plotly_chart(fig2)

if opcion == "Mapa Interactivo":
    st.title("Mapa Interactivo - Ubicación de Actores")
    
    if not df.empty:
        mapa = folium.Map(location=[df["Latitud"].mean(), df["Longitud"].mean()], zoom_start=6)

        for _, row in df.iterrows():
            color = "blue" if row["Tipo"] == "Factor" else "green" if row["Tipo"] == "Atractor" else "red"
            folium.Marker(
                [row["Latitud"], row["Longitud"]],
                popup=f"{row['Actor']} - {row['Objetivo']} ({row['Tipo']})",
                icon=folium.Icon(color=color),
            ).add_to(mapa)

        folium_static(mapa)
    else:
        st.warning("No hay datos disponibles. Ingrese información en la sección de 'Ingreso de Datos'.")
