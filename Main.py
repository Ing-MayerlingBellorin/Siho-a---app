import streamlit as st
import pandas as pd
from datetime import datetime
import io
from streamlit_gsheets import GSheetsConnection

# CONFIGURACIÓN TOTAL
st.set_page_config(page_title="SIHO-A Final", page_icon="🛡️", layout="wide")

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
                if u.lower() == "adm" and p == "1234":
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = u
                    st.rerun()
                else:
                    st.error("❌ Clave incorrecta")
else:
    # CONEXIÓN REFORZADA
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
    except:
        st.error("⚠️ Error de conexión. Revisa tus Secrets en Streamlit Cloud.")
        st.stop()

    menu = st.sidebar.radio("Menú:", ["Registro de Gestión", "Bitácora"])

    if menu == "Registro de Gestión":
        st.title("🛡️ Registro SIHO-A")
        
        # Conteo desde 01/01/2026
        dias = (datetime.now().date() - datetime(2026, 1, 1).date()).days
        st.success(f"🔥 {max(0, dias)} DÍAS SIN ACCIDENTES")

        with st.form("form_final", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                f_reg = st.date_input("Fecha", datetime.now())
                ubi = st.selectbox("Centro de Costo", ["Base - Caracas", "Base - Anaco", "Pariaguán", "El Tigre", "Morichal", "Troil-01", "Troil-02", "Troil-03", "Troil-04", "Troil-05", "Troil-06", "Troil-07", "Troil-08", "Troil-10"])
            with c2:
                act = st.selectbox("Actividad", ["Charla 5 min", "Inspección", "Dotación EPP", "Incidente"])
                cert = st.text_input("Certificaciones")
            with c3:
                e_cert = st.selectbox("Estatus Certificación", ["Vigente", "Vencida", "N/A"])
                pers = st.selectbox("Personal", ["CCP", "Supervisores", "Company", "Troil", "N/A"])
            
            desc = st.text_area("Descripción de la Gestión")
            foto = st.file_uploader("📸 Evidencia Fotográfica", type=["jpg", "png", "jpeg"])
            
            if st.form_submit_button("💾 GUARDAR Y SINCRONIZAR", use_container_width=True):
                try:
                    # Forzamos la lectura de la pestaña 'Datos'
                    df_old = conn.read(worksheet="Datos", ttl=0)
                    
                    nueva_fila = pd.DataFrame([{
                        "Fecha": f_reg.strftime('%Y-%m-%d'),
                        "Centro de Costo": ubi,
                        "Actividad": act,
                        "Responsable": st.session_state.usuario_actual,
                        "Descripción": desc,
                        "Certificaciones": cert,
                        "Estatus Certificación": e_cert,
                        "Evidencia Foto": foto.name if foto else "Sin foto"
                    }])
                    
                    df_new = pd.concat([df_old, nueva_fila], ignore_index=True)
                    conn.update(worksheet="Datos", data=df_new)
                    st.balloons()
                    st.success("✅ ¡Guardado con éxito!")
                except Exception as e:
                    st.error(f"❌ Error crítico: Asegúrate de que tu pestaña de Excel se llame exactamente 'Datos' (con D mayúscula).")

    else:
        st.title("📊 Bitácora")
        df = conn.read(worksheet="Datos", ttl=0)
        # DESCARGA EXCEL
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📥 Descargar Excel", output.getvalue(), "SIHO_Reporte.xlsx")
        st.info("💡 Para PDF: Presiona Ctrl+P y selecciona 'Guardar como PDF'")
        st.dataframe(df, use_container_width=True)
