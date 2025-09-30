import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.patches as patches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import io
from PIL import Image
import requests
from datetime import datetime
import base64

# Configuración de la página
st.set_page_config(
    page_title="⚽ Scout App - TOP 3 por Posición", 
    page_icon="⚽",
    layout="wide"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #4CAF50, #45a049);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .filter-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin-bottom: 15px;
    }
    .position-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 12px;
        margin: 2px;
    }
    .pos-gk { background-color: #FFD700; color: #000; }
    .pos-def { background-color: #4169E1; color: #fff; }
    .pos-mid { background-color: #32CD32; color: #fff; }
    .pos-att { background-color: #FF4500; color: #fff; }
</style>
""", unsafe_allow_html=True)

# Inicializar session state con formación 4-4-2
if 'formation' not in st.session_state:
    st.session_state.formation = {
        'GK': None,
        'CB1': None,
        'CB2': None,
        'RB': None,
        'LB': None,
        'CDM1': None,
        'CDM2': None,
        'RM': None,
        'LM': None,
        'ST1': None,
        'ST2': None
    }

if 'adding_player' not in st.session_state:
    st.session_state.adding_player = False

if 'selected_position' not in st.session_state:
    st.session_state.selected_position = None

# Header principal
st.markdown("""
<div class="main-header">
    <h1>⚽ SCOUT APP - EQUIPO 11 IDEAL</h1>
    <p>Selecciona jugadores y asígnalos a cualquier posición</p>
</div>
""", unsafe_allow_html=True)

# Función para cargar imagen desde URL
@st.cache_data
def load_image_from_url(url, size=(50, 50)):
    try:
        if pd.isna(url) or url == '':
            return None
        response = requests.get(url, timeout=5)
        img = Image.open(io.BytesIO(response.content))
        img = img.resize(size, Image.Resampling.LANCZOS)
        return img
    except:
        return None

# Función para extraer año de fecha
def extract_year_from_date(date_str):
    try:
        if pd.isna(date_str):
            return None
        if isinstance(date_str, datetime):
            return date_str.year
        date_obj = pd.to_datetime(date_str)
        return date_obj.year
    except:
        return None

# Función para detectar nombres de columnas
def detect_column_names(df):
    column_mapping = {
        'jugador': None,
        'posicion': None,
        'altura': None,
        'nacionalidad': None,
        'equipo': None,
        'logo_equipo': None,
        'liga': None,
        'fecha_nacimiento': None,
        'foto_jugador': None
    }
    
    columns_lower = {col.lower(): col for col in df.columns}
    
    for key in ['jugador', 'nombre', 'player', 'name']:
        if key in columns_lower:
            column_mapping['jugador'] = columns_lower[key]
            break
    
    for key in ['pos_principal', 'posicion', 'posición', 'position', 'pos']:
        if key in columns_lower:
            column_mapping['posicion'] = columns_lower[key]
            break
    
    for key in ['equipo', 'team', 'club']:
        if key in columns_lower:
            column_mapping['equipo'] = columns_lower[key]
            break
    
    for key in ['altura', 'height', 'alt']:
        if key in columns_lower:
            column_mapping['altura'] = columns_lower[key]
            break
    
    for key in ['areanacimiento_nombre', 'nacionalidad', 'nationality', 'pais']:
        if key in columns_lower:
            column_mapping['nacionalidad'] = columns_lower[key]
            break
    
    for key in ['urlimagen.y', 'logo_equipo', 'logo', 'team_logo']:
        if key in columns_lower:
            column_mapping['logo_equipo'] = columns_lower[key]
            break
    
    for key in ['liga', 'league', 'competition']:
        if key in columns_lower:
            column_mapping['liga'] = columns_lower[key]
            break
    
    for key in ['fechanacimiento', 'fecha_nacimiento', 'birthdate', 'birth_date']:
        if key in columns_lower:
            column_mapping['fecha_nacimiento'] = columns_lower[key]
            break
    
    for key in ['urlimagen.x', 'foto_jugador', 'photo', 'player_photo']:
        if key in columns_lower:
            column_mapping['foto_jugador'] = columns_lower[key]
            break
    
    return column_mapping

# Función para cargar Excel
def load_excel_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    col_map = detect_column_names(df)
    
    rename_dict = {}
    if col_map['jugador']:
        rename_dict[col_map['jugador']] = 'Jugador'
    if col_map['posicion']:
        rename_dict[col_map['posicion']] = 'Pos_Original'
    if col_map['equipo']:
        rename_dict[col_map['equipo']] = 'Equipo'
    if col_map['altura']:
        rename_dict[col_map['altura']] = 'altura'
    if col_map['nacionalidad']:
        rename_dict[col_map['nacionalidad']] = 'Nacionalidad'
    if col_map['logo_equipo']:
        rename_dict[col_map['logo_equipo']] = 'urlImagen.y'
    if col_map['liga']:
        rename_dict[col_map['liga']] = 'liga'
    if col_map['fecha_nacimiento']:
        rename_dict[col_map['fecha_nacimiento']] = 'fechaNacimiento'
    if col_map['foto_jugador']:
        rename_dict[col_map['foto_jugador']] = 'urlImagen.x'
    
    df = df.rename(columns=rename_dict)
    
    if 'fechaNacimiento' in df.columns:
        df['año_nacimiento'] = df['fechaNacimiento'].apply(extract_year_from_date)
        current_year = datetime.now().year
        df['edad'] = current_year - df['año_nacimiento']
    
    return df, col_map

# Sidebar para cargar datos
st.sidebar.header("📁 CARGAR DATOS")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo Excel", type=['xlsx', 'xls'])

if uploaded_file is not None:
    try:
        df, column_mapping = load_excel_data(uploaded_file)
        st.sidebar.success("✅ Archivo cargado!")
    except Exception as e:
        st.sidebar.error(f"❌ Error: {e}")
        st.stop()
else:
    st.sidebar.warning("⚠️ Sube tu Excel")
    st.stop()

# Filtros globales
st.sidebar.markdown('<div class="filter-box">', unsafe_allow_html=True)
st.sidebar.header("🔍 FILTROS")

ligas_disponibles = sorted(df['liga'].unique())
liga_seleccionada = st.sidebar.selectbox("📊 Liga:", ligas_disponibles)

df_liga = df[df['liga'] == liga_seleccionada]

if 'Nacionalidad' in df_liga.columns:
    nacionalidades = ['Todas'] + sorted(df_liga['Nacionalidad'].dropna().unique().tolist())
    nacionalidad_filtro = st.sidebar.selectbox("🌍 Nacionalidad:", nacionalidades)
    
    if nacionalidad_filtro != 'Todas':
        df_disponible = df_liga[df_liga['Nacionalidad'] == nacionalidad_filtro]
    else:
        df_disponible = df_liga
else:
    df_disponible = df_liga

st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Botón para limpiar
if st.sidebar.button("🗑️ LIMPIAR FORMACIÓN", type="secondary"):
    st.session_state.formation = {key: None for key in st.session_state.formation}
    st.rerun()

# Mapeo de posiciones a nombres legibles
POSITION_NAMES = {
    'GK': 'Arquero',
    'CB1': 'Defensor Central 1',
    'CB2': 'Defensor Central 2',
    'RB': 'Lateral Derecho',
    'LB': 'Lateral Izquierdo',
    'CDM1': 'Mediocampista Central 1',
    'CDM2': 'Mediocampista Central 2',
    'RM': 'Mediocampista Derecho',
    'LM': 'Mediocampista Izquierdo',
    'ST1': 'Delantero 1',
    'ST2': 'Delantero 2'
}

# Función para crear cancha interactiva
def create_pitch_visual(formation_dict, df):
    fig, ax = plt.subplots(figsize=(16, 11))
    pitch = Pitch(
        pitch_type='opta',
        pitch_color='#2d8f2d',
        line_color='white',
        linewidth=3
    )
    pitch.draw(ax=ax)
    
    # Posiciones en formación 4-4-2
    positions_coords = {
        'GK': (10, 50),
        'RB': (25, 85),
        'CB1': (25, 60),
        'CB2': (25, 40),
        'LB': (25, 15),
        'RM': (50, 85),
        'CDM1': (50, 60),
        'CDM2': (50, 40),
        'LM': (50, 15),
        'ST1': (80, 60),
        'ST2': (80, 40)
    }
    
    colors = {
        'GK': '#FFD700',
        'RB': '#4169E1', 'CB1': '#4169E1', 'CB2': '#4169E1', 'LB': '#4169E1',
        'RM': '#32CD32', 'CDM1': '#32CD32', 'CDM2': '#32CD32', 'LM': '#32CD32',
        'ST1': '#FF4500', 'ST2': '#FF4500'
    }
    
    for pos_id, (x, y) in positions_coords.items():
        player_name = formation_dict.get(pos_id)
        
        if player_name:
            player_data = df[df['Jugador'] == player_name]
            
            if not player_data.empty:
                player = player_data.iloc[0]
                
                circle = plt.Circle((x, y), 4, 
                                  color=colors[pos_id], 
                                  alpha=0.9, 
                                  zorder=10,
                                  edgecolor='white',
                                  linewidth=2)
                ax.add_patch(circle)
                
                ax.text(x, y-9, f"{player['Jugador']}", 
                       ha='center', va='top', 
                       fontsize=9, fontweight='bold',
                       color='white',
                       bbox=dict(boxstyle="round,pad=0.3", 
                               facecolor='black', 
                               alpha=0.8))
                
                info_parts = []
                if 'año_nacimiento' in player and not pd.isna(player['año_nacimiento']):
                    info_parts.append(f"({int(player['año_nacimiento'])})")
                if 'edad' in player and not pd.isna(player['edad']):
                    info_parts.append(f"{int(player['edad'])} años")
                
                info_text = " - ".join(info_parts) if info_parts else ""
                
                if info_text:
                    ax.text(x, y+9, info_text, 
                           ha='center', va='bottom',
                           fontsize=8,
                           color='white',
                           bbox=dict(boxstyle="round,pad=0.2", 
                                   facecolor=colors[pos_id], 
                                   alpha=0.9))
                
                if 'urlImagen.y' in player and not pd.isna(player['urlImagen.y']):
                    try:
                        logo_img = load_image_from_url(player['urlImagen.y'], size=(25, 25))
                        if logo_img:
                            import numpy as np
                            logo_array = np.array(logo_img)
                            imagebox = OffsetImage(logo_array, zoom=0.5)
                            ab = AnnotationBbox(imagebox, (x+6, y+6), frameon=False)
                            ax.add_artist(ab)
                    except:
                        pass
        else:
            # Posición vacía
            circle = plt.Circle((x, y), 4, 
                              color='#555', 
                              alpha=0.5, 
                              zorder=5,
                              edgecolor='white',
                              linewidth=2,
                              linestyle='dashed')
            ax.add_patch(circle)
            
            ax.text(x, y, pos_id, 
                   ha='center', va='center',
                   fontsize=10,
                   color='white',
                   fontweight='bold')
    
    ax.text(50, 108, f"EQUIPO 11 IDEAL", 
           ha='center', va='bottom',
           fontsize=18, fontweight='bold',
           color='white')
    
    ax.text(50, 104, f"{liga_seleccionada.upper()}", 
           ha='center', va='bottom',
           fontsize=14, fontweight='bold',
           color='white')
    
    fecha_actual = datetime.now().strftime("%m/%Y")
    ax.text(90, -3, fecha_actual, 
           ha='center', va='bottom',
           fontsize=10,
           color='white')
    
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 112)
    ax.axis('off')
    
    return fig

# Layout principal
col_left, col_main = st.columns([1, 3])

with col_left:
    st.markdown("### ➕ AGREGAR JUGADOR")
    
    # Búsqueda de jugador
    buscar = st.text_input("🔍 Buscar jugador:", placeholder="Nombre del jugador...")
    
    # Filtro por equipo
    if 'Equipo' in df_disponible.columns:
        equipos = ['Todos'] + sorted(df_disponible['Equipo'].dropna().unique().tolist())
        equipo_filtro = st.selectbox("🏆 Filtrar por equipo:", equipos)
    else:
        equipo_filtro = 'Todos'
    
    # Aplicar filtros
    df_filtered = df_disponible.copy()
    
    if buscar:
        df_filtered = df_filtered[
            df_filtered['Jugador'].str.contains(buscar, case=False, na=False)
        ]
    
    if 'Equipo' in df_filtered.columns and equipo_filtro != 'Todos':
        df_filtered = df_filtered[df_filtered['Equipo'] == equipo_filtro]
    
    # Lista de jugadores
    if not df_filtered.empty:
        jugadores_list = df_filtered['Jugador'].tolist()
        
        # Crear opciones con info
        opciones = []
        for _, player in df_filtered.iterrows():
            nombre = player['Jugador']
            info_parts = []
            if 'Equipo' in player and not pd.isna(player['Equipo']):
                info_parts.append(str(player['Equipo']))
            if 'Pos_Original' in player and not pd.isna(player['Pos_Original']):
                info_parts.append(str(player['Pos_Original']))
            
            if info_parts:
                opciones.append(f"{nombre} ({' - '.join(info_parts)})")
            else:
                opciones.append(nombre)
        
        jugador_seleccionado = st.selectbox(
            "Selecciona jugador:",
            opciones,
            key="jugador_select"
        )
        
        # Extraer nombre real
        jugador_nombre = jugador_seleccionado.split(' (')[0]
        
        # Selector de posición
        posicion_destino = st.selectbox(
            "Asignar a posición:",
            list(POSITION_NAMES.keys()),
            format_func=lambda x: POSITION_NAMES[x],
            key="pos_select"
        )
        
        if st.button("✅ AGREGAR A FORMACIÓN", type="primary", use_container_width=True):
            st.session_state.formation[posicion_destino] = jugador_nombre
            st.success(f"✅ {jugador_nombre} agregado!")
            st.rerun()
    else:
        st.info("No se encontraron jugadores con esos filtros")
    
    st.markdown("---")
    
    # Lista de jugadores en formación
    st.markdown("### 📋 FORMACIÓN ACTUAL")
    
    filled_positions = {k: v for k, v in st.session_state.formation.items() if v}
    
    if filled_positions:
        for pos_id, player_name in filled_positions.items():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{POSITION_NAMES[pos_id]}**")
                st.caption(player_name)
            with col2:
                if st.button("❌", key=f"remove_{pos_id}"):
                    st.session_state.formation[pos_id] = None
                    st.rerun()
        
        st.metric("👥 Jugadores", f"{len(filled_positions)}/11")
    else:
        st.info("⚠️ No hay jugadores en la formación")

with col_main:
    st.markdown("### 🏟️ CANCHA - FORMACIÓN 4-4-2")
    
    fig = create_pitch_visual(st.session_state.formation, df)
    st.pyplot(fig)
    
    # Botones de exportación
    col_exp1, col_exp2, col_exp3 = st.columns(3)
    
    with col_exp1:
        if st.button("📄 EXPORTAR PNG", type="primary", use_container_width=True):
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight',
                       facecolor='#2d8f2d', edgecolor='none')
            img_buffer.seek(0)
            
            b64 = base64.b64encode(img_buffer.getvalue()).decode()
            href = f'<a href="data:image/png;base64,{b64}" download="equipo_11_ideal_{liga_seleccionada.replace(" ", "_")}.png">📥 Descargar PNG</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.success("✅ Imagen generada!")
    
    with col_exp2:
        if st.button("📋 EXPORTAR CSV", type="secondary", use_container_width=True):
            lista_jugadores = []
            for pos_id, player_name in st.session_state.formation.items():
                if player_name:
                    player_data = df[df['Jugador'] == player_name]
                    if not player_data.empty:
                        p = player_data.iloc[0]
                        player_dict = {
                            'Posición': POSITION_NAMES[pos_id],
                            'Jugador': player_name
                        }
                        if 'Equipo' in p:
                            player_dict['Equipo'] = p['Equipo']
                        if 'año_nacimiento' in p:
                            player_dict['Año'] = p['año_nacimiento']
                        if 'edad' in p:
                            player_dict['Edad'] = p['edad']
                        lista_jugadores.append(player_dict)
            
            if lista_jugadores:
                df_export = pd.DataFrame(lista_jugadores)
                csv = df_export.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="formacion_{liga_seleccionada.replace(" ", "_")}.csv">📥 Descargar CSV</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("✅ CSV generado!")
    
    with col_exp3:
        if st.button("🔄 VISTA RÁPIDA", type="secondary", use_container_width=True):
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>⚽ Scout App 2025 | Sistema rápido de formación 4-4-2</p>
</div>
""", unsafe_allow_html=True)