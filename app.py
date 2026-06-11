import streamlit as st
import json
import os
import uuid
from typing import Dict, List, Any

# ==========================================
# CONFIGURACIÓN DE PÁGINA (Debe ir primero)
# ==========================================
st.set_page_config(
    page_title="Centro de Operaciones TIC",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# ESTILOS CSS PERSONALIZADOS (Look SaaS)
# ==========================================
def inject_custom_css():
    st.markdown("""
        <style>
            /* Ocultar elementos predeterminados de Streamlit */
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            
            /* Ajustar espaciado superior */
            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }
            
            /* Estilizar botones para que parezcan de panel de control */
            .stButton > button {
                border-radius: 6px;
                transition: all 0.2s ease;
            }
            .stButton > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# GESTOR DE DATOS (Persistencia y Auto-curación)
# ==========================================
DATA_FILE = "data.json"

DEFAULT_DATA = {
    "categories": ["Zoho Desk", "Telefonía Avaya", "Redes Cisco", "General TIC"],
    "scripts": []
}

class DataManager:
    @staticmethod
    def load_data() -> Dict[str, Any]:
        """Carga datos con tolerancia a fallos. Se recupera de JSON corruptos o faltantes."""
        if not os.path.exists(DATA_FILE):
            DataManager.save_data(DEFAULT_DATA)
            return DEFAULT_DATA.copy()
        
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Autocomprobación de estructura básica
            if "categories" not in data or "scripts" not in data:
                raise ValueError("Estructura JSON inválida.")
            return data
            
        except (json.JSONDecodeError, ValueError, Exception):
            # En caso de error fatal, reconstruir para evitar caída de la app
            st.toast("⚠️ Se detectó un problema con la base de datos local. Usando estructura por defecto.", icon="⚠️")
            return DEFAULT_DATA.copy()

    @staticmethod
    def save_data(data: Dict[str, Any]):
        """Guarda los datos en el disco de forma segura."""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            st.error(f"Error crítico al guardar datos: {e}")

    @staticmethod
    def sync_state():
        """Sincroniza session_state con el archivo físico."""
        DataManager.save_data({
            "categories": st.session_state['categories'],
            "scripts": st.session_state['scripts']
        })

# Inicializar estado
if 'initialized' not in st.session_state:
    db_data = DataManager.load_data()
    st.session_state['categories'] = db_data['categories']
    st.session_state['scripts'] = db_data['scripts']
    st.session_state['initialized'] = True

# ==========================================
# MODO OPERACIÓN
# ==========================================
def render_operation_mode():
    st.title("⚡ Centro de Operaciones TIC")
    
    # Métricas rápidas
    col1, col2, col3 = st.columns(3)
    col1.metric("Plantillas Activas", len(st.session_state['scripts']))
    col2.metric("Categorías", len(st.session_state['categories']))
    col3.metric("Estado del Sistema", "Online 🟢")
    
    st.divider()
    
    # Barra de búsqueda y filtros
    search_col, filter_col = st.columns([2, 1])
    with search_col:
        search_term = st.text_input("🔍 Buscar plantilla o script...", placeholder="Ej: configuración J139, OSPF, Zoho...")
    with filter_col:
        selected_category = st.selectbox("📂 Filtrar por Categoría", ["Todas"] + st.session_state['categories'])

    # Filtrar lógica
    filtered_scripts = [
        s for s in st.session_state['scripts']
        if (selected_category == "Todas" or s['category'] == selected_category) and
           (search_term.lower() in s['title'].lower() or search_term.lower() in s['content'].lower() or search_term.lower() in s.get('tags', '').lower())
    ]

    if not filtered_scripts:
        st.info("No se encontraron resultados para la búsqueda o filtro actual.")
        return

    # Renderizado tipo Tarjetas (Masonry simplificado en columnas)
    cols = st.columns(2)
    for i, script in enumerate(filtered_scripts):
        with cols[i % 2]:
            # Usar st.container con border para emular tarjetas SaaS
            with st.container(border=True):
                st.subheader(script['title'])
                st.caption(f"🏷️ {script['category']} | 🔑 Tags: {script.get('tags', 'N/A')}")
                
                # El bloque de código proporciona un botón nativo de copiado
                st.code(script['content'], language="markdown")

# ==========================================
# MODO ADMINISTRACIÓN
# ==========================================
def render_admin_mode():
    st.title("⚙️ Administración del Sistema")
    
    tab1, tab2, tab3 = st.tabs(["📝 Nueva Plantilla", "✏️ Editar / Eliminar Plantillas", "📁 Gestionar Categorías"])
    
    # --- TAB 1: Nueva Plantilla ---
    with tab1:
        with st.form("new_script_form", clear_on_submit=True):
            st.write("### Crear nueva plantilla")
            new_title = st.text_input("Título descriptivo")
            new_cat = st.selectbox("Categoría", st.session_state['categories'])
            new_tags = st.text_input("Etiquetas (separadas por coma)")
            new_content = st.text_area("Contenido / Script", height=200)
            
            if st.form_submit_button("Guardar Plantilla", type="primary"):
                if new_title and new_content:
                    new_item = {
                        "id": str(uuid.uuid4()),
                        "title": new_title,
                        "category": new_cat,
                        "tags": new_tags,
                        "content": new_content
                    }
                    st.session_state['scripts'].append(new_item)
                    DataManager.sync_state()
                    st.success("Plantilla guardada exitosamente.")
                else:
                    st.error("El título y el contenido son obligatorios.")

    # --- TAB 2: Editar / Eliminar ---
    with tab2:
        if not st.session_state['scripts']:
            st.info("No hay plantillas registradas.")
        else:
            script_titles = {s['id']: f"{s['title']} ({s['category']})" for s in st.session_state['scripts']}
            selected_script_id = st.selectbox("Selecciona una plantilla para modificar", options=list(script_titles.keys()), format_func=lambda x: script_titles[x])
            
            if selected_script_id:
                # Encontrar el script actual
                target_script = next(s for s in st.session_state['scripts'] if s['id'] == selected_script_id)
                
                with st.form("edit_script_form"):
                    edit_title = st.text_input("Título", value=target_script['title'])
                    edit_cat = st.selectbox("Categoría", st.session_state['categories'], index=st.session_state['categories'].index(target_script['category']) if target_script['category'] in st.session_state['categories'] else 0)
                    edit_tags = st.text_input("Etiquetas", value=target_script.get('tags', ''))
                    edit_content = st.text_area("Contenido", value=target_script['content'], height=200)
                    
                    col_save, col_del = st.columns([1, 1])
                    with col_save:
                        if st.form_submit_button("Actualizar Plantilla", type="primary"):
                            target_script.update({
                                "title": edit_title,
                                "category": edit_cat,
                                "tags": edit_tags,
                                "content": edit_content
                            })
                            DataManager.sync_state()
                            st.success("Plantilla actualizada.")
                            st.rerun()
                    with col_del:
                        delete_confirm = st.checkbox("Confirmar eliminación")
                        if st.form_submit_button("🗑️ Eliminar") and delete_confirm:
                            st.session_state['scripts'] = [s for s in st.session_state['scripts'] if s['id'] != selected_script_id]
                            DataManager.sync_state()
                            st.success("Plantilla eliminada.")
                            st.rerun()

    # --- TAB 3: Categorías ---
    with tab3:
        st.write("### Categorías Actuales")
        for cat in st.session_state['categories']:
            col_name, col_btn = st.columns([4, 1])
            col_name.write(f"- {cat}")
            if col_btn.button("🗑️", key=f"del_cat_{cat}", help="Eliminar categoría"):
                # Verificar si está en uso
                in_use = any(s['category'] == cat for s in st.session_state['scripts'])
                if in_use:
                    st.error(f"No se puede eliminar '{cat}'. Hay plantillas usándola.")
                else:
                    st.session_state['categories'].remove(cat)
                    DataManager.sync_state()
                    st.success(f"Categoría '{cat}' eliminada.")
                    st.rerun()
        
        st.divider()
        with st.form("new_cat_form", clear_on_submit=True):
            new_category = st.text_input("Añadir nueva categoría")
            if st.form_submit_button("Añadir Categoría"):
                if new_category and new_category not in st.session_state['categories']:
                    st.session_state['categories'].append(new_category)
                    DataManager.sync_state()
                    st.success("Categoría añadida.")
                    st.rerun()
                elif new_category in st.session_state['categories']:
                    st.warning("La categoría ya existe.")

# ==========================================
# CONTROLADOR PRINCIPAL Y NAVEGACIÓN
# ==========================================
def main():
    inject_custom_css()
    
    with st.sidebar:
        st.title("🛠️ TIC Hub")
        st.write("Panel de Control")
        mode = st.radio("Modo de Trabajo", ["⚡ Operación", "⚙️ Administración"])
        
        st.divider()
        st.caption("Sistema de respuestas rápidas y soporte nivel 1/2.")
        
    if mode == "⚡ Operación":
        render_operation_mode()
    else:
        render_admin_mode()

if __name__ == "__main__":
    main()
