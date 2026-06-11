import streamlit as st
import json
import os
import uuid

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(page_title="Mis Scripts Rápidos", page_icon="⚡", layout="wide")

# CSS Avanzado para mejorar la interfaz (Tarjetas, centrado y sombras)
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {padding-top: 2rem; padding-bottom: 2rem;}
        
        /* Centrar y mejorar el diseño de las pestañas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            justify-content: center;
            border-bottom: 2px solid #f0f2f6;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 1.15rem;
            font-weight: 600;
            padding-bottom: 1rem;
        }
        
        /* Efecto Hover elegante para las tarjetas (st.container border) */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 8px;
            background-color: #ffffff;
            transition: all 0.2s ease-in-out;
        }
        /* El modo oscuro de Streamlit invertirá estos colores automáticamente de forma elegante */
        @media (prefers-color-scheme: light) {
            div[data-testid="stVerticalBlockBorderWrapper"]:hover {
                box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
                border-color: #FF4B4B; /* Acento sutil de Streamlit */
            }
        }
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
# CABECERA PRINCIPAL
# ==========================================
st.markdown("<h1 style='text-align: center; margin-bottom: 1rem;'>⚡ Centro de Operaciones</h1>", unsafe_allow_html=True)

# Crear las dos pestañas principales
tab_operacion, tab_admin = st.tabs(["🔍 Buscar y Copiar", "⚙️ Administrar Scripts"])

# ------------------------------------------
# PESTAÑA 1: OPERACIÓN (BÚSQUEDA Y COPIA EN GRID)
# ------------------------------------------
with tab_operacion:
    st.write("") # Espaciador
    
    # Barra de búsqueda centrada para mejor UX
    col_space1, col_search, col_space2 = st.columns([1, 2, 1])
    with col_search:
        search_term = st.text_input("Buscador", placeholder="🔍 Buscar por título... (Ej. Avaya, Zoho, OSPF)", label_visibility="collapsed").strip().lower()
    
    st.write("---")
    
    # Filtrar scripts
    filtered_scripts = [s for s in st.session_state.scripts if search_term in s['title'].lower()]
    
    if not filtered_scripts:
        st.info("No tienes scripts guardados o ninguno coincide con tu búsqueda.")
    else:
        # DISTRIBUCIÓN EN CUADRÍCULA (2 COLUMNAS)
        # Esto evita que el script ocupe toda la pantalla y mejora la lectura
        cols = st.columns(2)
        
        for index, script in enumerate(filtered_scripts):
            # Alternar entre la columna 0 y 1
            with cols[index % 2]:
                with st.container(border=True):
                    st.markdown(f"#### {script['title']}")
                    # wrap_lines=True es la magia: fuerza al texto a bajar, evitando el scroll horizontal infinito
                    st.code(script['content'], language="markdown", wrap_lines=True)

# ------------------------------------------
# PESTAÑA 2: ADMINISTRACIÓN (PANTALLA DIVIDIDA)
# ------------------------------------------
with tab_admin:
    st.write("") # Espaciador
    
    # Distribuir la administración en dos columnas: Agregar (Izquierda) y Editar/Eliminar (Derecha)
    col_add, col_edit = st.columns([1, 1], gap="large")
    
    # LADO IZQUIERDO: AGREGAR NUEVO
    with col_add:
        st.subheader("➕ Agregar Nuevo Script")
        with st.form("add_form", clear_on_submit=True):
            new_title = st.text_input("Título del script", placeholder="Ej: Pasos para migrar J139")
            new_content = st.text_area("Contenido / Código", height=250, placeholder="Escribe aquí el procedimiento o script...")
            
            if st.form_submit_button("💾 Guardar Nuevo Script", type="primary", use_container_width=True):
                if new_title and new_content:
                    st.session_state.scripts.insert(0, {
                        "id": str(uuid.uuid4()),
                        "title": new_title,
                        "content": new_content
                    })
                    sync_data()
                    st.success("✅ Script agregado exitosamente.")
                    st.rerun()
                else:
                    st.error("⚠️ El título y el contenido son obligatorios.")
    
    # LADO DERECHO: EDITAR / ELIMINAR
    with col_edit:
        st.subheader("✏️ Modificar o Eliminar")
        
        if not st.session_state.scripts:
            st.info("No hay scripts registrados para administrar.")
        else:
            # Iterar sobre los scripts dentro de acordeones (expanders) para no saturar visualmente
            for script in st.session_state.scripts:
                with st.expander(f"📄 {script['title']}"):
                    edit_title = st.text_input("Título", value=script['title'], key=f"t_{script['id']}")
                    edit_content = st.text_area("Contenido", value=script['content'], height=150, key=f"c_{script['id']}")
                    
                    # Botones de acción en sub-columnas
                    btn_col1, btn_col2 = st.columns([1, 1])
                    with btn_col1:
                        if st.button("Actualizar", key=f"save_{script['id']}", use_container_width=True):
                            for s in st.session_state.scripts:
                                if s['id'] == script['id']:
                                    s['title'] = edit_title
                                    s['content'] = edit_content
                            sync_data()
                            st.success("Actualizado.")
                            st.rerun()
                    with btn_col2:
                        if st.button("Eliminar", key=f"del_{script['id']}", type="primary", use_container_width=True):
                            st.session_state.scripts = [s for s in st.session_state.scripts if s['id'] != script['id']]
                            sync_data()
                            st.rerun()
