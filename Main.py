import streamlit as st
import pandas as pd
from datetime import datetime
import time
import io
from streamlit_gsheets import GSheetsConnection

# 1. SEGURIDAD
USUARIOS = {"adm": "1234", "supervisor1": "1234"}

st.set_page_config(page_title="Gestión SIHO-A", page_icon="🛡️", layout="wide")

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align:center;'>🛡️ SIHO-A: ACCESO</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            u = st.text_input("Usuario")
            p = st.text_input("Clave", type="password")
            if st.button("INGRESAR", use_container_width=True):
                if u in USUARIOS and USUARIOS[u] == p:
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = u
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")

else:
    # Conexión principal
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Sidebar
    st.sidebar.title(f"👤 {st.session_state.usuario_actual}")
    if st.sidebar.button("🔒 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
    
    menu = st.sidebar.radio("Navegación:", ["Registro de Gestión", "Bitácora y Reportes"])

    if menu == "Registro de Gestión":
        st.title("🛡️ Gestión SIHO-A: Registro Diario")
        
        # Conteo de seguridad (Ajustado a tus fotos)
        dias = (datetime.now().date() - datetime(2026, 1, 1).date()).days
        st.success(f"✅ {max(0, dias)} DÍAS SIN ACCIDENTES")

        with st.form("form_siho", clear_on_submit=True):
            st.markdown("### 📝 Datos del Registro")
            c1, c2, c3 = st.columns(3)
            with c1:
                f_reg = st.date_input("Fecha", datetime.now())
                ubi = st.selectbox("Ubicación", ["Base - Caracas", "Base - Anaco", "Pariaguán", "El Tigre", "Morichal", "Troil-01", "Troil-02", "Troil-03", "Troil-04", "Troil-05"])
                resp = st.text_input("Responsable", value=st.session_state.usuario_actual, disabled=True)
            with c2:
                act = st.selectbox("Actividad", ["Charla 5 min", "Inspección", "Dotación EPP", "Incidente"])
                cert = st.text_input("Certificación / Item")
                e_cert = st.selectbox("Estatus Certificación", ["Vigente", "Vencida", "N/A"])
            with c3:
                dot = st.text_input("Dotación / EPP")
                e_dot = st.selectbox("Estatus Dotación", ["Vigente", "Vencida", "N/A"])
                pers = st.selectbox("Personal Involucrado", ["CCP", "Supervisores", "Company", "Troil", "N/A"])
            
            desc = st.text_area("Descripción Detallada")
            foto = st.file_uploader("📸 Cargar Evidencia Fotográfica", type=["jpg", "png", "jpeg"])
            
            if st.form_submit_button("💾 GUARDAR Y SINCRONIZAR", use_container_width=True):
                try:
                    # Lectura sin caché para evitar errores de red
                    df_old = conn.read(worksheet="Datos", ttl=0)
                    
                    # MAPEO DE COLUMNAS SIMPLIFICADO PARA EVITAR ERRORES
                    nueva_fila = pd.DataFrame([{
                        "Fecha": f_reg.strftime('%Y-%m-%d'),
                        "Centro de Costo": ubi,
                        "Actividad": act,
                        "Responsable ": resp,
                        "Descripción": desc,
                        "Certificaciones": cert,
                        "Estatus Certificacion": e_cert,
                        "Dotación": dot,
                        "Estatus Dotación": e_dot,
                        "Personal": pers,
                        "Evidencia Foto": foto.name if foto else "Sin foto"
                    }])
                    
                    df_new = pd.concat([df_old, nueva_fila], ignore_index=True)
                    conn.update(worksheet="Datos", data=df_new)
                    st.balloons()
                    st.success("✅ ¡Sincronizado con éxito en la base de datos!")
                except Exception as e:
                    st.error("❌ ERROR DE NOMBRES: Revisa que la primera fila de tu Excel tenga exactamente estos nombres: Fecha, Centro de Costo, Actividad, Responsable , Descripción, Certificaciones, Estatus Certificacion, Dotación, Estatus Dotación, Personal, Evidencia Foto")

    else:
        st.title("📊 Bitácora")
        try:
            df = conn.read(worksheet="Datos", ttl=0)
            st.dataframe(df, use_container_width=True)
            
            # Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 Descargar Reporte Excel", output.getvalue(), "SIHO_Reporte.xlsx")
        except:
            st.info("Aún no hay registros sincronizados.")
