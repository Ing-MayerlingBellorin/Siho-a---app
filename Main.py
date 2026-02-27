import streamlit as st
import pandas as pd
from datetime import datetime
import io
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SIHO-A Operaciones", page_icon="🛡️", layout="wide")

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- ACCESO ---
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align:center;'>🛡️ SIHO-A: INGRESO</h1>", unsafe_allow_html=True)
    with st.container(border=True):
        u = st.text_input("Usuario")
        p = st.text_input("Clave", type="password")
        if st.button("INGRESAR", use_container_width=True):
            if u.lower() == "adm" and p == "1234":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
else:
    # CONEXIÓN USANDO SERVICE ACCOUNT (Configurada en tus Secrets)
    conn = st.connection("gsheets", type=GSheetsConnection)

    menu = st.sidebar.radio("Navegación", ["Registro", "Bitácora"])

    if menu == "Registro":
        st.title("🛡️ Gestión SIHO-A 2026")
        
        # Conteo de seguridad
        dias = (datetime.now().date() - datetime(2026, 1, 1).date()).days
        st.success(f"🔥 {max(0, dias)} DÍAS SIN ACCIDENTES")

        with st.form("registro_siho"):
            c1, c2, c3 = st.columns(3)
            with c1:
                f_reg = st.date_input("Fecha", datetime.now())
                ubi = st.selectbox("Centro de Costo", ["Base - Caracas", "Base - Anaco", "Pariaguán", "El Tigre", "Morichal", "Troil-01", "Troil-02", "Troil-03", "Troil-04", "Troil-05", "Troil-06", "Troil-07", "Troil-08", "Troil-09", "Troil-10"])
            with c2:
                act = st.selectbox("Actividad", ["Charla 5 min", "Inspección", "Dotación EPP", "Incidente"])
                cert = st.text_input("Certificaciones")
            with c3:
                e_cert = st.selectbox("Estatus Certificación", ["Vigente", "Vencida", "N/A"])
                pers = st.selectbox("Personal", ["CCP", "Supervisores", "Company", "Troil", "N/A"])
            
            desc = st.text_area("Descripción Detallada")
            foto = st.file_uploader("📸 Foto de Evidencia", type=["jpg", "png", "jpeg"])
            
            if st.form_submit_button("💾 GUARDAR REGISTRO"):
                try:
                    # Lectura y Limpieza
                    df_old = conn.read(worksheet="Datos", ttl=0)
                    df_old.columns = df_old.columns.str.strip()
                    
                    nueva_fila = pd.DataFrame([{
                        "Fecha": f_reg.strftime('%Y-%m-%d'),
                        "Centro de Costo": ubi,
                        "Actividad": act,
                        "Responsable": "adm",
                        "Descripción": desc,
                        "Certificaciones": cert,
                        "Estatus Certificación": e_cert,
                        "Evidencia Foto": foto.name if foto else "Sin foto"
                    }])
                    
                    df_new = pd.concat([df_old, nueva_fila], ignore_index=True)
                    conn.update(worksheet="Datos", data=df_new)
                    st.balloons()
                    st.success("✅ Sincronizado exitosamente con el Servidor")
                except Exception as e:
                    st.error(f"Error: {e}. ¿Compartiste el Excel con el correo de servicio?")

    else:
        st.title("📊 Bitácora de Gestión")
        df = conn.read(worksheet="Datos", ttl=0)
        st.dataframe(df, use_container_width=True)
        
        # EXPORTAR
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📥 Descargar Excel", output.getvalue(), "Reporte.xlsx")

