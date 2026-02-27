import streamlit as st
import pandas as pd
from datetime import datetime
import time
import io
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN Y SEGURIDAD
st.set_page_config(page_title="Gestión SIHO-A", page_icon="🛡️", layout="wide")
USUARIOS = {"adm": "1234", "supervisor1": "1234"}

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- PANTALLA DE LOGIN ---
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
    # CONEXIÓN A LA BASE DE DATOS
    conn = st.connection("gsheets", type=GSheetsConnection)

    # BARRA LATERAL
    st.sidebar.title(f"👤 {st.session_state.usuario_actual}")
    if st.sidebar.button("🔒 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
    
    menu = st.sidebar.radio("Navegación:", ["Registro de Gestión", "Bitácora y Reportes"])

    # --- REGISTRO DIARIO ---
    if menu == "Registro de Gestión":
        st.title("🛡️ Registro de Gestión SIHO-A")
        
        # CONTEO DE SEGURIDAD (Desde 01/01/2026 como pediste)
        dias = (datetime.now().date() - datetime(2026, 1, 1).date()).days
        st.success(f"🔥 {max(0, dias)} DÍAS SIN ACCIDENTES (Desde 01/01/2026)")

        with st.form("form_siho", clear_on_submit=True):
            st.markdown("### 📝 Ingreso de Datos")
            c1, c2, c3 = st.columns(3)
            with c1:
                f_reg = st.date_input("Fecha", datetime.now())
                # UBICACIONES ACTUALIZADAS
                ubi = st.selectbox("Centro de Costo", ["Base - Caracas", "Base - Anaco", "Pariaguán", "El Tigre", "Morichal", 
                                                 "Troil-01", "Troil-02", "Troil-03", "Troil-04", "Troil-05", 
                                                 "Troil-06", "Troil-07", "Troil-08", "Troil-09", "Troil-10"])
                resp = st.text_input("Responsable", value=st.session_state.usuario_actual, disabled=True)
            with c2:
                act = st.selectbox("Actividad", ["Charla 5 min", "Inspección", "Dotación EPP", "Incidente"])
                cert = st.text_input("Certificaciones")
                e_cert = st.selectbox("Estatus Certificación", ["Vigente", "Vencida", "N/A"])
            with c3:
                dot = st.text_input("Dotación")
                e_dot = st.selectbox("Estatus Dotación", ["Vigente", "Vencida", "N/A"])
                pers = st.selectbox("Personal", ["CCP", "Supervisores", "Company", "Troil", "N/A"])
            
            desc = st.text_area("Descripción de la Gestión")
            foto = st.file_uploader("📸 Cargar Evidencia Fotográfica", type=["jpg", "png", "jpeg"])
            
            if st.form_submit_button("💾 GUARDAR Y SINCRONIZAR", use_container_width=True):
                try:
                    # Leemos el Excel actual
                    df_old = conn.read(worksheet="Datos", ttl=0)
                    
                    # CREAMOS LA NUEVA FILA CON LOS NOMBRES EXACTOS DE TU EXCEL
                    nueva_fila = pd.DataFrame([{
                        "Fecha": f_reg.strftime('%Y-%m-%d'),
                        "Centro de Costo": ubi,
                        "Actividad": act,
                        "Responsable": resp,
                        "Descripción": desc,
                        "Certificaciones": cert,
                        "Estatus Certificación": e_cert,
                        "Dotación": dot,
                        "Estatus Dotación": e_dot,
                        "Personal": pers,
                        "Evidencia Foto": foto.name if foto else "Sin foto"
                    }])
                    
                    # UNIMOS Y SUBIMOS
                    df_new = pd.concat([df_old, nueva_fila], ignore_index=True)
                    conn.update(worksheet="Datos", data=df_new)
                    
                    st.balloons()
                    st.success("✅ ¡Sincronizado con éxito!")
                except Exception as e:
                    st.error("❌ ERROR DE CONEXIÓN: Verifica que la pestaña de tu Excel se llame 'Datos' y los títulos coincidan.")

    # --- BITÁCORA Y REPORTES ---
    else:
        st.title("📊 Bitácora y Reportes")
        try:
            df = conn.read(worksheet="Datos", ttl=0)
            
            # Botón para descargar EXCEL
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 Descargar Reporte (Excel)", output.getvalue(), "SIHO_Reporte.xlsx", use_container_width=True)
            
            st.info("💡 Para PDF: Presiona 'Ctrl + P' en tu teclado.")
            st.dataframe(df.sort_values(by="Fecha", ascending=False), use_container_width=True)
        except:
            st.info("No hay datos registrados todavía.")
