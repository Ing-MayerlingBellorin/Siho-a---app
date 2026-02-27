import streamlit as st
import pandas as pd
from datetime import datetime
import time
import io
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# --- 1. BASE DE DATOS DE USUARIOS (PRUEBA PILOTO) ---
# Clave unificada para todos: 1234
CLAVE_PILOTO = "1234"

USUARIOS_AUTORIZADOS = {
    "adm": CLAVE_PILOTO,
    "supervisor1": CLAVE_PILOTO,
    "supervisor2": CLAVE_PILOTO,
    "inspeccion": CLAVE_PILOTO
}

# 2. IDENTIDAD CORPORATIVA
st.set_page_config(page_title="Gestión SIHO-A", page_icon="🛡️", layout="wide")

# Inicializar estado de autenticación
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'usuario_actual' not in st.session_state:
    st.session_state.usuario_actual = ""

# --- FUNCIÓN DE LOGIN ---
def login():
    st.markdown("""
        <div style="text-align:center; padding: 20px;">
            <h1 style="color:#1e3d59; font-size: 50px;">🛡️</h1>
            <h1 style="color:#1e3d59;">SIHO-A: FASE PILOTO</h1>
            <p style="color:#6c757d;">Acceso Restringido - Personal Autorizado</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        with st.container(border=True):
            user_input = st.text_input("Usuario Asignado")
            pw_input = st.text_input("Clave de Prueba", type="password")
            
            if st.button("ACCEDER AL PANEL", use_container_width=True):
                if user_input in USUARIOS_AUTORIZADOS and USUARIOS_AUTORIZADOS[user_input] == pw_input:
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = user_input
                    st.success(f"✅ Sesión iniciada como: {user_input}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Usuario no válido o clave incorrecta.")

# --- LÓGICA DE CONTROL DE ACCESO ---
if not st.session_state.autenticado:
    login()
else:
    # --- CONTENIDO DE LA APLICACIÓN ---
    
    def cargar_datos():
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df = conn.read(worksheet="Datos")
            if not df.empty and 'Fecha' in df.columns:
                df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
            return df
        except Exception:
            return pd.DataFrame()

    df_principal = cargar_datos()

    # Barra lateral
    st.sidebar.markdown(f"👤 **Usuario Activo:** `{st.session_state.usuario_actual}`")
    if st.sidebar.button("🔒 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.usuario_actual = ""
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛡️ CONTROL OPERATIVO")
    seccion = st.sidebar.radio("Ir a:", ["Registro Diario", "Bitácora e Indicadores"])

    centros = ["Base Morichal", "Base Caracas", "Base pariaguan", "Base Anaco", "Base El Tigre", 
               "Troil 1", "Troil 2", "Troil 3", "Troil 4", "Troil 5", "Troil 6", 
               "Troil 7", "Troil 8", "Troil 9", "Troil 10", "Troil 11"]

    # --- SECCIÓN: REGISTRO ---
    if seccion == "Registro Diario":
        st.title("🛡️ Registro de Gestión SIHO-A")
        
        if 'f_inicio' not in st.session_state:
            st.session_state.f_inicio = datetime(2026, 1, 1).date()
        
        col_f1, col_f2 = st.columns([1, 2])
        with col_f1:
            f_inc = st.date_input("Inicio de conteo:", st.session_state.f_inicio)
            st.session_state.f_inicio = f_inc
        
        dias = (datetime.now().date() - f_inc).days
        with col_f2:
            st.markdown(f"""
                <div style="background-color:#f0f2f6;padding:15px;border-radius:10px;border-left:5px solid #28a745;text-align:center;">
                    <h2 style="color:#1e3d59;margin:0;font-size:20px;">ESTADO DE SEGURIDAD</h2>
                    <h1 style="color:#28a745;margin:0;font-size:40px;">{dias} DÍAS SIN ACCIDENTES</h1>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        with st.form("form_siho", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                f_reg = st.date_input("Fecha", datetime.now())
                ubi = st.selectbox("Ubicación", centros)
                # El nombre del responsable se bloquea con el usuario que inició sesión
                resp = st.text_input("Responsable", value=st.session_state.usuario_actual, disabled=True)
            with c2:
                cert = st.text_input("Certificación / Item")
                e_cert = st.selectbox("Estatus Certificación", ["Vigente", "Vencida", "N/A"])
                pers = st.selectbox("Personal", ["CCP", "Supervisores", "Company", "Troil", "N/A"])
            with c3:
                dot = st.text_input("Dotación / EPP")
                e_dot = st.selectbox("Estatus Dotación", ["Vigente", "Vencida", "N/A"])
                act = st.selectbox("Actividad", ["Charla 5 min", "Inspección", "Dotación", "Incidente", "N/A"])
            
            desc = st.text_area("Descripción de la Gestión")
            foto = st.file_uploader("📸 Cargar Evidencia (Foto)", type=["jpg", "png", "jpeg"])
            
            btn_save = st.form_submit_button("💾 GUARDAR REGISTRO", use_container_width=True)

        if btn_save:
            if resp and desc:
                try:
                    nombre_foto = foto.name if foto else "Sin foto"
                    nuevo_reg = pd.DataFrame([{
                        "Fecha": f_reg.strftime('%Y-%m-%d'),
                        "Centro de Costo": ubi,
                        "Responsable": resp,
                        "Certificación": cert,
                        "Estatus Certificación": e_cert,
                        "Personal": pers,
                        "Dotación": dot,
                        "Estatus Dotación": e_dot,
                        "Actividad": act,
                        "Descripción": desc,
                        "Evidencia": nombre_foto
                    }])

                    conn = st.connection("gsheets", type=GSheetsConnection)
                    df_old = conn.read(worksheet="Datos")
                    df_new = pd.concat([df_old, nuevo_reg], ignore_index=True)
                    conn.update(worksheet="Datos", data=df_new)
                    
                    with st.spinner('Sincronizando...'):
                        time.sleep(1)
                    
                    if act == "Incidente":
                        st.warning(f"⚠️ REGISTRO DE INCIDENTE ARCHIVADO.")
                    else:
                        st.success(f"✅ GESTIÓN GUARDADA CORRECTAMENTE.")
                    st.toast('Base de Datos SIHO-A Actualizada', icon='🛡️')
                    
                except Exception as e:
                    st.error(f"❌ Error de conexión con la base de datos.")
            else:
                st.error("⚠️ Complete la descripción antes de guardar.")

    # --- SECCIÓN: BITÁCORA ---
    else:
        st.title("📊 Historial e Indicadores de Gestión")
        if not df_principal.empty:
            c_s, c_d = st.columns([1, 1])
            with c_s:
                if st.button("🔄 Actualizar Tabla"):
                    st.cache_data.clear()
                    st.rerun()
            
            # Preparar Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_principal.to_excel(writer, index=False, sheet_name='SIHO_DATA')
            
            with c_d:
                st.download_button(
                    label="📥 Descargar Reporte Completo (Excel)",
                    data=output.getvalue(),
                    file_name=f'Reporte_SIHO_{datetime.now().strftime("%Y%m%d")}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

            df_ord = df_principal.sort_values(by='Fecha', ascending=False)
            st.dataframe(df_ord, use_container_width=True)
            
            st.markdown("---")
            g1, g2 = st.columns(2)
            with g1:
                fig = px.pie(df_ord, names='Estatus Dotación', title="Nivel de Cumplimiento EPP")
                st.plotly_chart(fig, use_container_width=True)
            with g2:
                st.subheader("Actividad por Centro de Costo")
                st.bar_chart(df_ord['Centro de Costo'].value_counts())
        else:
            st.warning("⚠️ No hay datos disponibles para mostrar.")
