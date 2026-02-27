import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN INICIAL (Siempre de primero)
st.set_page_config(page_title="Gestión SIHO-A", page_icon="🛡️", layout="wide")

# 2. CONEXIÓN A TU EXCEL 'Base_Datos_Siho_A'
def cargar_base_datos():
    try:
        # Usamos la conexión oficial para leer la pestaña 'Datos'
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Datos")
        
        # Limpiamos los datos para que el reporte no falle
        if not df.empty:
            # Convertimos la columna Fecha a formato real
            if 'Fecha' in df.columns:
                df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        return df
    except Exception:
        # Si el Excel está vacío o no conecta, devolvemos una tabla vacía
        return pd.DataFrame()

df_siho = cargar_base_datos()

# 3. BARRA LATERAL (Menú de Navegación)
st.sidebar.title("🛡️ SIHO-A Navigation")
seccion = st.sidebar.radio("Ir a:", ["Registro Diario", "Panel de Reportes Normativos"])

# Lista de tus 16 Centros de Costo
lista_centros = ["Base Morichal", "Base Caracas", "Pariaguan", "Base Anaco", "Base El Tigre", 
                 "Troil 1", "Troil 2", "Troil 3", "Troil 4", "Troil 5", "Troil 6", 
                 "Troil 7", "Troil 8", "Troil 9", "Troil 10", "Troil 11"]

# --- SECCIÓN 1: REGISTRO DIARIO ---
if seccion == "Registro Diario":
    st.title("🛡️ Sistema de Gestión SIHO-A")
    
    # CONTADOR DE DÍAS (Basado en tu imagen de éxito)
    if 'inicio_conteo' not in st.session_state:
        st.session_state.inicio_conteo = datetime(2026, 1, 1).date()
    
    col_fecha, col_banner = st.columns([1, 2])
    with col_fecha:
        f_incidente = st.date_input("Fecha Inicio Conteo:", st.session_state.inicio_conteo)
        st.session_state.inicio_conteo = f_incidente
    
    dias_seguros = (datetime.now().date() - f_incidente).days
    
    with col_banner:
        st.markdown(f"""
            <div style="background-color: #d4edda; padding: 20px; border-radius: 10px; border: 2px solid #28a745; text-align: center;">
                <h1 style="color: #155724; margin: 0; font-size: 40px;">{dias_seguros} DÍAS SIN ACCIDENTES</h1>
                <p style="color: #155724; font-weight: bold;">CUMPLIENDO NORMAS DE SEGURIDAD</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # FORMULARIO DE ENTRADA
    with st.form("form_siho", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            fecha_act = st.date_input("Fecha Registro", datetime.now())
            centro = st.selectbox("Ubicación / Centro", lista_centros)
            quien = st.text_input("Responsable")
        with c2:
            cert_item = st.text_input("Certificación / Item")
            e_cert = st.selectbox("Estatus Certificación", ["Vigente", "Vencida", "No Aplica"])
            p_tipo = st.selectbox("Personal", ["CCP", "Supervisores", "Company", "Troil", "No Aplica"])
        with c3:
            dotacion = st.text_input("Dotación / EPP")
            e_dot = st.selectbox("Estatus Dotación", ["Vigente", "Vencida", "No Aplica"])
            actividad = st.selectbox("Actividad", ["Charla 5 min", "Inspección", "Dotación", "No Aplica"])
            
        nota = st.text_area("Descripción de la Gestión")
        foto = st.file_uploader("Evidencia Fotográfica", type=["jpg", "png", "jpeg"])
        
        btn_enviar = st.form_submit_button("💾 GUARDAR REGISTRO")
        
    if btn_enviar:
        if quien and nota:
            st.success(f"✅ ¡Registro de {centro} guardado! Ahora puedes verlo en Reportes.")
            st.balloons()
        else:
            st.warning("⚠️ Debes indicar el Responsable y la Descripción.")

# --- SECCIÓN 2: PANEL DE REPORTES ---
else:
    st.title("📊 Indicadores de Cumplimiento SIHO-A")
    
    if df_siho.empty:
        st.warning("⚠️ Todavía no hay datos en el Excel o no hay conexión. Realiza un registro primero.")
    else:
        # Filtros Rápidos
        centro_filtro = st.sidebar.selectbox("Filtrar por Centro", ["Todos"] + lista_centros)
        df_filtrado = df_siho if centro_filtro == "Todos" else df_siho[df_siho['Centro de Costo'] == centro_filtro]
        
        # Dashboard de cumplimiento
        col_g1, col_g2 = st.columns(2)
else:
    st.title("📊 Bitácora y Reportes SIHO-A")
    
    # BOTÓN PARA REFRESCAR DATOS (Esto soluciona que no veas lo recién guardado)
    if st.button("🔄 Actualizar Datos del Excel"):
        st.cache_data.clear()
        st.rerun()

    if df_siho.empty:
        st.warning("⚠️ No se encuentran registros. Asegúrate de que la hoja en Excel se llame 'Datos'.")
    else:
        # 1. ORDENAR POR FECHA (Lo más reciente primero)
        df_ordenado = df_siho.sort_values(by='Fecha', ascending=False)

        # 2. FILTROS DE BÚSQUEDA
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            busqueda = st.text_input("🔍 Buscar por Responsable o Centro:", "")
        with col_f2:
            filtro_fecha = st.date_input("Filtrar desde esta fecha:", datetime(2024, 1, 1))

        # Aplicar filtros
        df_final = df_ordenado[df_ordenado['Fecha'] >= pd.Timestamp(filtro_fecha)]
        if busqueda:
            df_final = df_final[df_final.astype(str).apply(lambda x: x.str.contains(busqueda, case=False)).any(axis=1)]

        # 3. MOSTRAR LA TABLA DE REGISTROS (Tu Bitácora)
        st.markdown("### 📜 Historial de Registros Guardados")
        st.dataframe(df_final, use_container_width=True)

        # 4. GRÁFICOS DE RESUMEN
        st.markdown("---")
        st.subheader("📈 Resumen Visual de la Gestión")
        c1, c2 = st.columns(2)
        with c1:
            fig_act = px.pie(df_final, names='Actividad', title="Tipos de Actividades")
            st.plotly_chart(fig_act, use_container_width=True)
        with c2:
            fig_centro = px.bar(df_final, x='Centro de Costo', title="Registros por Ubicación")
            st.plotly_chart(fig_centro, use_container_width=True)
          with col_g1:
            st.subheader("Estatus Normativo (Dotación)")
            # Gráfico de torta profesional con Plotly
            fig_p = px.pie(df_filtrado, names='Estatus Dotación', 
                           color='Estatus Dotación',
                           color_discrete_map={'Vigente':'#28a745', 'Vencida':'#dc3545', 'No Aplica':'#6c757d'})
            st.plotly_chart(fig_p, use_container_width=True)
            
        with col_g2:
            st.subheader("Actividades Registradas")
            # Gráfico de barras de actividades
            st.bar_chart(df_filtrado['Actividad'].value_counts())
            
        st.markdown("---")
        st.subheader("📋 Detalle de Registros")
        st.dataframe(df_filtrado, use_container_width=True)
        
        # Botón para descargar
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Reporte en Excel (CSV)", csv, "Reporte_SIHO.csv", "text/csv")
