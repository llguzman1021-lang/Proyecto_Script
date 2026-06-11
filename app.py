import streamlit as st
import json
import os
import uuid

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(page_title="Centro de Operaciones", page_icon="⚡", layout="wide")

# CSS Avanzado
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {padding-top: 2rem; padding-bottom: 2rem;}
        .stTabs [data-baseweb="tab-list"] {gap: 2rem; justify-content: center; border-bottom: 2px solid #f0f2f6;}
        .stTabs [data-baseweb="tab"] {font-size: 1.15rem; font-weight: 600; padding-bottom: 1rem;}
        div[data-testid="stVerticalBlockBorderWrapper"] {border-radius: 8px; background-color: #ffffff; transition: all 0.2s ease-in-out;}
        @media (prefers-color-scheme: light) {
            div[data-testid="stVerticalBlockBorderWrapper"]:hover {box-shadow: 0px 4px 12px rgba(0,0,0,0.08); border-color: #FF4B4B;}
        }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "data.json"
RECOVERY_EMAIL = "llguzman1021@gmail.com"

# ==========================================
# GESTOR DE DATOS Y MIGRACIÓN
# ==========================================
def load_data():
    default_data = {"pin": "1010", "scripts": []}
    if not os.path.exists(DATA_FILE):
        return default_data
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return {"pin": "1010", "scripts": data}
            return data
    except:
        return default_data

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error al guardar: {e}")

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def sync_data():
    save_data(st.session_state.db)

# ==========================================
# SISTEMA DE LOGIN (AUTH)
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.write("") 
    st.write("") 
    st.markdown("<h2 style='text-align: center;'>🔒 Acceso Restringido</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Centro de Operaciones TIC</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            with st.form("login_form"):
                pin_input = st.text_input("Ingresa tu PIN", type="password", placeholder="****")
                submit = st.form_submit_button("Ingresar", type="primary", use_container_width=True)
                
                if submit:
                    if pin_input == st.session_state.db.get("pin", "1010"):
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        st.error("❌ PIN incorrecto.")
        
       # Flujo de recuperación simplificado
        if st.button("¿Olvidaste tu PIN?", use_container_width=True):
            st.info(f"📧 Por favor, comunícate con el administrador del sistema para solicitar la recuperación del acceso a la cuenta: **{RECOVERY_EMAIL}**.")
    
    st.stop()

# ==========================================
# PANTALLA PRINCIPAL (ACCESO CONCEDIDO)
# ==========================================
col_title, col_logout = st.columns([5, 1])
with col_title:
    st.markdown("<h1 style='margin-bottom: 0;'>⚡ Centro de Operaciones</h1>", unsafe_allow_html=True)
with col_logout:
    st.write("") 
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

tab_operacion, tab_admin = st.tabs(["🔍 Buscar y Copiar", "⚙️ Administrar Sistema"])

# ------------------------------------------
# PESTAÑA 1: OPERACIÓN
# ------------------------------------------
with tab_operacion:
    st.write("")
    col_space1, col_search, col_space2 = st.columns([1, 2, 1])
    with col_search:
        # Texto del buscador actualizado según tu solicitud
        search_term = st.text_input("Buscador", placeholder="Buscar por título...", label_visibility="collapsed").strip().lower()
    
    st.write("---")
    
    filtered_scripts = [s for s in st.session_state.db['scripts'] if search_term in s['title'].lower()]
    
    if not filtered_scripts:
        st.info("No tienes scripts guardados o ninguno coincide con tu búsqueda.")
    else:
        cols = st.columns(2)
        for index, script in enumerate(filtered_scripts):
            with cols[index % 2]:
                with st.container(border=True):
                    st.markdown(f"#### {script['title']}")
                    st.code(script['content'], language="markdown", wrap_lines=True)

# ------------------------------------------
# PESTAÑA 2: ADMINISTRACIÓN
# ------------------------------------------
with tab_admin:
    st.write("")
    
    # Distribución equilibrada para la gestión de scripts
    col_add, col_edit = st.columns(2, gap="large")
    
    with col_add:
        st.subheader("➕ Agregar Nuevo Script")
        with st.form("add_form", clear_on_submit=True):
            new_title = st.text_input("Título del script", placeholder="Ej: Pasos para migrar J139")
            new_content = st.text_area("Contenido / Código", height=250)
            
            if st.form_submit_button("💾 Guardar Script", type="primary", use_container_width=True):
                if new_title and new_content:
                    st.session_state.db['scripts'].insert(0, {
                        "id": str(uuid.uuid4()),
                        "title": new_title,
                        "content": new_content
                    })
                    sync_data()
                    st.success("✅ Script agregado exitosamente.")
                    st.rerun()
                else:
                    st.error("⚠️ Título y contenido son obligatorios.")

    with col_edit:
        st.subheader("✏️ Modificar o Eliminar")
        
        if not st.session_state.db['scripts']:
            st.info("No hay scripts registrados.")
        else:
            for script in st.session_state.db['scripts']:
                with st.expander(f"📄 {script['title']}"):
                    edit_title = st.text_input("Título", value=script['title'], key=f"t_{script['id']}")
                    edit_content = st.text_area("Contenido", value=script['content'], height=150, key=f"c_{script['id']}")
                    
                    btn_col1, btn_col2 = st.columns([1, 1])
                    with btn_col1:
                        if st.button("Actualizar", key=f"save_{script['id']}", use_container_width=True):
                            for s in st.session_state.db['scripts']:
                                if s['id'] == script['id']:
                                    s['title'] = edit_title
                                    s['content'] = edit_content
                            sync_data()
                            st.success("Actualizado.")
                            st.rerun()
                    with btn_col2:
                        if st.button("Eliminar", key=f"del_{script['id']}", type="primary", use_container_width=True):
                            st.session_state.db['scripts'] = [s for s in st.session_state.db['scripts'] if s['id'] != script['id']]
                            sync_data()
                            st.rerun()
    
    # Separador visual
    st.divider()
    
    # SECCIÓN DE SEGURIDAD INDEPENDIENTE EN LA PARTE INFERIOR
    st.subheader("🔑 Seguridad")
    with st.expander("Cambiar PIN de Acceso"):
        with st.form("change_pin_form"):
            current_pin = st.text_input("PIN Actual", type="password")
            new_pin = st.text_input("Nuevo PIN", type="password")
            
            if st.form_submit_button("Actualizar PIN", type="primary"):
                if current_pin != st.session_state.db.get("pin", "1010"):
                    st.error("❌ El PIN actual es incorrecto.")
                elif len(new_pin) < 4:
                    st.error("⚠️ El nuevo PIN debe tener al menos 4 caracteres.")
                else:
                    st.session_state.db['pin'] = new_pin
                    sync_data()
                    st.success("✅ PIN actualizado correctamente.")
