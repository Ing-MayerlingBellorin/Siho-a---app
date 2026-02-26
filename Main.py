import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="SIHO-A Dashboard", page_icon="🛡️", layout="wide")

# --- CONEXIÓN AL EXCEL (Solo lectura para reportes) ---
def cargar_datos():
    try:
        creds = st.secrets["GOOGLE_CREDENTIALS"]
        # Aquí se usa gspread para leer tu archivo Base_Datos_Siho_A
        from gspread_pandas import Spread
        spread = Spread("Base_Datos_Siho_A", creds=creds)
        df = spread.sheet_to_df(sheet="Datos", index=0)
        # Convertimos la columna fecha a formato fecha real para poder filtrar
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        return df
    except:
        return pd.DataFrame()

df_principal = cargar_datos()

# --- NAVEGACIÓN ---
st.sidebar.title("Menú SIHO-A")
opcion = st.sidebar.radio("Selecciona una opción:", ["Registro Diario", "Panel de Reportes"])

if opcion == "Registro Diario":
    st.title("🛡️ Sistema de Gestión SIHO-A")
    # (Aquí mantienes tu código del contador de días y el formulario que ya funciona)
    st.info("Utiliza el menú lateral para ir a la sección de Reportes.")

else:
    st.title("📊 Panel de Indicadores y Reportes")
    
    if df_principal.empty:
        st.warning("No se encontraron datos en el Excel para mostrar reportes.")
    else:
        # --- FILTROS ---
        st.sidebar.header("Filtros de Reporte")
        
        # Filtro de Fecha
        fecha_min = df_principal['fecha'].min()
        fecha_max = df_principal['fecha'].max()
        rango_fecha = st.sidebar.date_input("Rango de fechas", [fecha_min, fecha_max])
        
        # Filtro de Centro de Costo
        centros = ["Todos"] + sorted(df_principal['centro de costo'].unique().tolist())
        centro_sel = st.sidebar.selectbox("Seleccionar Centro de Costo", centros)
        
        # Aplicar filtros al DataFrame
        df_filtrado = df_principal.copy()
        if len(rango_fecha) == 2:
            df_filtrado = df_filtrado[(df_filtrado['fecha'] >= pd.Timestamp(rango_fecha[0])) & 
                                     (df_filtrado['fecha'] <= pd.Timestamp(rango_fecha[1]))]
        
        if centro_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado['centro de costo'] == centro_sel]

        # --- MÉTRICAS EN GRANDE ---
        m1, m2, m3 = st.columns(3)
        with m1:
            total_charlas = len(df_filtrado[df_filtrado['categoría'].str.contains('Charla', case=False, na=False)])
            st.metric("Total Charlas dadas", total_charlas)
        with m2:
            # [span_1](start_span)Filtro basado en tu columna 'estatus'[span_1](end_span)
            vencidas = len(df_filtrado[df_filtrado['estatus'].str.contains('Vencid', case=False, na=False)])
            st.metric("Dotaciones Vencidas", vencidas, delta_color="inverse")
        with m3:
            st.metric("Registros en este periodo", len(df_filtrado))

        # --- GRÁFICO DE BARRAS ---
        st.subheader(f"Resumen de Actividades en {centro_sel}")
        resumen_act = df_filtrado['categoría'].value_counts()
        st.bar_chart(resumen_act)

        # --- TABLA DE DATOS DETALLADA ---
        st.subheader("📋 Detalle de los registros")
        st.dataframe(df_filtrado, use_container_width=True)
        
        # Botón para descargar el reporte filtrado
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar este reporte (Excel/CSV)", csv, "reporte_siho.csv", "text/csv")
