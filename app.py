import streamlit as st
import json
import os
import uuid

# ==========================================
# CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="Mis Scripts Rápidos", page_icon="⚡", layout="wide")

# CSS mínimo para ocultar la marca de Streamlit y maximizar el espacio
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {padding-top: 1.5rem; padding-bottom: 1.5rem;}
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "data.json"

# ==========================================
# GESTOR DE DATOS SIMPLIFICADO
# ==========================================
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error al guardar: {e}")

if 'scripts' not in st.session_state:
    st.session_state.scripts = load_data()

def sync_data():
    save_data(st.session_state.scripts)

# ==========================================
# BARRA LATERAL: AGREGAR NUEVO
# ==========================================
with st.sidebar:
    st.header("➕ Nuevo Script")
    with st.form("add_form", clear_on_submit=True):
        new_title = st.text_input("Título del script")
        new_content = st.text_area("Contenido / Código", height=200)
        
        if st.form_submit_button("Guardar Script", type="primary"):
            if new_title and new_content:
                st.session_state.scripts.insert(0, {  # Insertar al inicio para verlo rápido
                    "id": str(uuid.uuid4()),
                    "title": new_title,
                    "content": new_content
                })
                sync_data()
                st.success("Agregado exitosamente.")
                st.rerun()
            else:
                st.error("Título y contenido son obligatorios.")

# ==========================================
# PANTALLA PRINCIPAL: BUSCAR Y COPIAR
# ==========================================
st.title("⚡ Mis Scripts")

# Barra de búsqueda principal
search_term = st.text_input("🔍 Buscar por título...", "").strip().lower()
st.divider()

# Filtrar scripts
filtered_scripts = [s for s in st.session_state.scripts if search_term in s['title'].lower()]

if not filtered_scripts:
    st.info("No tienes scripts guardados o ninguno coincide con la búsqueda.")

# Mostrar scripts (Prioridad: visualización y botón de copiar)
for script in filtered_scripts:
    with st.container(border=True):
        st.subheader(script['title'])
        
        # El bloque de código trae su propio botón nativo de copiar en la esquina superior derecha
        st.code(script['content'], language="markdown")
        
        # Opciones de edición ocultas para no estorbar la lectura
        with st.expander("⚙️ Modificar / Eliminar"):
            edit_title = st.text_input("Título", value=script['title'], key=f"t_{script['id']}")
            edit_content = st.text_area("Contenido", value=script['content'], height=150, key=f"c_{script['id']}")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("💾 Guardar Cambios", key=f"save_{script['id']}"):
                    for s in st.session_state.scripts:
                        if s['id'] == script['id']:
                            s['title'] = edit_title
                            s['content'] = edit_content
                    sync_data()
                    st.rerun()
            with col2:
                if st.button("🗑️ Eliminar Script", key=f"del_{script['id']}", type="primary"):
                    st.session_state.scripts = [s for s in st.session_state.scripts if s['id'] != script['id']]
                    sync_data()
                    st.rerun()
