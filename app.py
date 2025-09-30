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
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .filter-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin-bottom: 15px;
    }
    .player-card {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        border-left: 4px solid #4CAF50;
    }
    .position-section {
        background-color: #e9ecef;
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'selected_players' not in st.session_state:
    st.session_state.selected_players = {
        'Arquero': [],
        'Defensor Central': [],
        'Lateral Izquierdo': [],
        'Lateral Derecho': [],
        'Mediocampista': [],
        'Delantero': []
    }

# Header principal
st.markdown("""
<div class="main-header">
    <h1>⚽ SCOUT APP - EQUIPO 11 IDEAL</h1>
    <p>Selecciona manualmente tu TOP 3 por posición</p>
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

# Función para detectar nombres de columnas automáticamente
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
    
    # Detectar columna de jugador
    for key in ['jugador', 'nombre', 'player', 'name']:
        if key in columns_lower:
            column_mapping['jugador'] = columns_lower[key]
            break
    
    # Detectar columna de posición
    for key in ['pos_principal', 'posicion', 'posición', 'position', 'pos']:
        if key in columns_lower:
            column_mapping['posicion'] = columns_lower[key]
            break
    
    # Detectar columna de equipo
    for key in ['equipo', 'team', 'club']:
        if key in columns_lower:
            column_mapping['equipo'] = columns_lower[key]
            break
    
    # Detectar columna de altura
    for key in ['altura', 'height', 'alt']:
        if key in columns_lower:
            column_mapping['altura'] = columns_lower[key]
            break
    
    # Detectar columna de nacionalidad
    for key in ['areanacimiento_nombre', 'nacionalidad', 'nationality', 'pais']:
        if key in columns_lower:
            column_mapping['nacionalidad'] = columns_lower[key]
            break
    
    # Detectar columna de logo equipo
    for key in ['urlimagen.y', 'logo_equipo', 'logo', 'team_logo']:
        if key in columns_lower:
            column_mapping['logo_equipo'] = columns_lower[key]
            break
    
    # Detectar columna de liga
    for key in ['liga', 'league', 'competition']:
        if key in columns_lower:
            column_mapping['liga'] = columns_lower[key]
            break
    
    # Detectar columna de fecha nacimiento
    for key in ['fechanacimiento', 'fecha_nacimiento', 'birthdate', 'birth_date']:
        if key in columns_lower:
            column_mapping['fecha_nacimiento'] = columns_lower[key]
            break
    
    # Detectar columna de foto jugador
    for key in ['urlimagen.x', 'foto_jugador', 'photo', 'player_photo']:
        if key in columns_lower:
            column_mapping['foto_jugador'] = columns_lower[key]
            break
    
    return column_mapping

# Función para cargar Excel con detección automática
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
        st.sidebar.success("✅ Archivo cargado correctamente!")
        
        with st.sidebar.expander("🔍 Columnas detectadas"):
            for key, value in column_mapping.items():
                if value:
                    st.text(f"{key}: ✅ {value}")
                else:
                    st.text(f"{key}: ❌ No detectada")
        
    except Exception as e:
        st.sidebar.error(f"❌ Error al cargar archivo: {e}")
        st.stop()
else:
    st.sidebar.warning("⚠️ Por favor sube tu archivo Excel para continuar")
    st.info("👆 Sube tu archivo Excel en el panel lateral izquierdo")
    st.stop()

# Filtros globales
st.sidebar.markdown('<div class="filter-box">', unsafe_allow_html=True)
st.sidebar.header("🔍 FILTROS GLOBALES")

ligas_disponibles = sorted(df['liga'].unique())
liga_seleccionada = st.sidebar.selectbox("📊 Seleccionar Liga:", ligas_disponibles)

df_liga = df[df['liga'] == liga_seleccionada]

# Mostrar cantidad de jugadores en la liga
st.sidebar.metric("👥 Jugadores disponibles", len(df_liga))

if 'Nacionalidad' in df_liga.columns:
    nacionalidades = ['Todas'] + sorted(df_liga['Nacionalidad'].dropna().unique().tolist())
    nacionalidad_filtro = st.sidebar.selectbox("🌍 Filtrar por Nacionalidad:", nacionalidades)
    
    if nacionalidad_filtro != 'Todas':
        df_disponible = df_liga[df_liga['Nacionalidad'] == nacionalidad_filtro]
        st.sidebar.caption(f"🔎 {len(df_disponible)} jugadores de {nacionalidad_filtro}")
    else:
        df_disponible = df_liga
else:
    df_disponible = df_liga

st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Botón para limpiar selecciones
if st.sidebar.button("🗑️ LIMPIAR TODAS LAS SELECCIONES", type="secondary"):
    st.session_state.selected_players = {
        'Arquero': [],
        'Defensor Central': [],
        'Lateral Izquierdo': [],
        'Lateral Derecho': [],
        'Mediocampista': [],
        'Delantero': []
    }
    st.rerun()

# Función para crear la cancha con jugadores
def create_pitch_with_players(selected_dict, df):
    fig, ax = plt.subplots(figsize=(16, 11))
    pitch = Pitch(
        pitch_type='opta',
        pitch_color='#2d8f2d',
        line_color='white',
        linewidth=3
    )
    pitch.draw(ax=ax)
    
    positions = {
        'Arquero': [(10, 50)],
        'Defensor Central': [(25, 35), (25, 50), (25, 65)],
        'Lateral Izquierdo': [(25, 15)],
        'Lateral Derecho': [(25, 85)],
        'Mediocampista': [(50, 30), (50, 50), (50, 70)],
        'Delantero': [(80, 35), (80, 50), (80, 65)]
    }
    
    colors = {
        'Arquero': '#FFD700',
        'Defensor Central': '#4169E1',
        'Lateral Izquierdo': '#4169E1',
        'Lateral Derecho': '#4169E1',
        'Mediocampista': '#32CD32',
        'Delantero': '#FF4500'
    }
    
    for position, coords in positions.items():
        if position in selected_dict and selected_dict[position]:
            player_names = selected_dict[position]
            for i, (x, y) in enumerate(coords[:len(player_names)]):
                if i < len(player_names):
                    player_data = df[df['Jugador'] == player_names[i]]
                    
                    if not player_data.empty:
                        player = player_data.iloc[0]
                        
                        circle = plt.Circle((x, y), 4, 
                                          color=colors[position], 
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
                        
                        info_text = " - ".join(info_parts) if info_parts else "N/A"
                        
                        ax.text(x, y+9, info_text, 
                               ha='center', va='bottom',
                               fontsize=8,
                               color='white',
                               bbox=dict(boxstyle="round,pad=0.2", 
                                       facecolor=colors[position], 
                                       alpha=0.9))
                        
                        if 'urlImagen.y' in player and not pd.isna(player['urlImagen.y']) and player['urlImagen.y'] != '':
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
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🎯 SELECCIÓN MANUAL DE JUGADORES")
    st.info("💡 Selecciona hasta 3 jugadores por posición. La posición original es solo referencia.")
    
    posiciones = ['Arquero', 'Defensor Central', 'Lateral Izquierdo', 
                 'Lateral Derecho', 'Mediocampista', 'Delantero']
    
    for posicion in posiciones:
        with st.expander(f"⚽ {posicion}", expanded=len(st.session_state.selected_players[posicion]) > 0):
            
            # Filtro de búsqueda por nombre
            col_search, col_equipo = st.columns([3, 2])
            
            with col_search:
                search_key = f"search_{posicion}"
                buscar_nombre = st.text_input(
                    "🔍 Buscar jugador:", 
                    key=search_key,
                    placeholder="Nombre del jugador...",
                    label_visibility="collapsed"
                )
            
            with col_equipo:
                if 'Equipo' in df_disponible.columns:
                    equipos = ['Todos'] + sorted(df_disponible['Equipo'].dropna().unique().tolist())
                    equipo_filtro = st.selectbox(
                        "🏆 Filtrar por equipo:",
                        equipos,
                        key=f"equipo_{posicion}",
                        label_visibility="collapsed"
                    )
        
        # Aplicar filtros
        df_filtered = df_disponible.copy()
        
        if buscar_nombre:
            df_filtered = df_filtered[
                df_filtered['Jugador'].str.contains(buscar_nombre, case=False, na=False)
            ]
        
        if 'Equipo' in df_filtered.columns and equipo_filtro != 'Todos':
            df_filtered = df_filtered[df_filtered['Equipo'] == equipo_filtro]
        
        # Crear lista de jugadores disponibles
        jugadores_disponibles = df_filtered['Jugador'].tolist()
        
        # Agregar info de posición original si existe
        if 'Pos_Original' in df_filtered.columns:
            jugadores_con_pos = [
                f"{row['Jugador']} ({row['Pos_Original']})" 
                if not pd.isna(row['Pos_Original']) 
                else row['Jugador']
                for _, row in df_filtered.iterrows()
            ]
        else:
            jugadores_con_pos = jugadores_disponibles
        
        # Multiselect para elegir hasta 3 jugadores
        selected = st.multiselect(
            f"✅ Elegir jugadores para {posicion}:",
            jugadores_con_pos,
            default=[
                f"{j} ({df_disponible[df_disponible['Jugador']==j]['Pos_Original'].iloc[0]})" 
                if 'Pos_Original' in df_disponible.columns and not df_disponible[df_disponible['Jugador']==j].empty
                and not pd.isna(df_disponible[df_disponible['Jugador']==j]['Pos_Original'].iloc[0])
                else j
                for j in st.session_state.selected_players[posicion] 
                if j in jugadores_disponibles
            ],
            max_selections=3,
            key=f"select_{posicion}",
            help="Selecciona máximo 3 jugadores"
        )
        
        # Extraer solo los nombres (quitar la posición entre paréntesis)
        selected_names = [s.split(' (')[0] for s in selected]
        st.session_state.selected_players[posicion] = selected_names
        
        # Mostrar seleccionados con info
        if selected_names:
            st.success(f"✅ {len(selected_names)}/3 seleccionados")
            for idx, name in enumerate(selected_names, 1):
                player_info = df_disponible[df_disponible['Jugador'] == name]
                if not player_info.empty:
                    p = player_info.iloc[0]
                    
                    col_num, col_info = st.columns([1, 11])
                    with col_num:
                        st.markdown(f"**#{idx}**")
                    with col_info:
                        info_parts = [f"**{name}**"]
                        
                        detail_parts = []
                        if 'Equipo' in p and not pd.isna(p['Equipo']):
                            detail_parts.append(f"🏆 {p['Equipo']}")
                        if 'edad' in p and not pd.isna(p['edad']):
                            detail_parts.append(f"🎂 {int(p['edad'])} años")
                        if 'Pos_Original' in p and not pd.isna(p['Pos_Original']):
                            detail_parts.append(f"📍 Pos. Original: {p['Pos_Original']}")
                        
                        st.markdown(f"{' '.join(info_parts)}")
                        if detail_parts:
                            st.caption(" | ".join(detail_parts))
        else:
            st.warning("⚠️ No hay jugadores seleccionados para esta posición")

with col2:
    st.subheader("🏟️ CANCHA INTERACTIVA")
    
    # Contar jugadores seleccionados
    total_selected = sum(len(players) for players in st.session_state.selected_players.values())
    
    if total_selected > 0:
        fig = create_pitch_with_players(st.session_state.selected_players, df)
        st.pyplot(fig)
        
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            if st.button("📄 EXPORTAR PNG", type="primary"):
                img_buffer = io.BytesIO()
                fig.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight',
                           facecolor='#2d8f2d', edgecolor='none')
                img_buffer.seek(0)
                
                b64 = base64.b64encode(img_buffer.getvalue()).decode()
                href = f'<a href="data:image/png;base64,{b64}" download="equipo_11_ideal_{liga_seleccionada.replace(" ", "_")}.png">📥 Descargar PNG</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("✅ Imagen PNG generada!")
        
        with col_export2:
            if st.button("📋 EXPORTAR LISTA"):
                lista_jugadores = []
                for pos, players in st.session_state.selected_players.items():
                    for player_name in players:
                        player_data = df[df['Jugador'] == player_name]
                        if not player_data.empty:
                            p = player_data.iloc[0]
                            player_dict = {
                                'Posición_Seleccionada': pos,
                                'Jugador': player_name
                            }
                            if 'Pos_Original' in p:
                                player_dict['Posición_Original'] = p['Pos_Original']
                            if 'Equipo' in p:
                                player_dict['Equipo'] = p['Equipo']
                            if 'año_nacimiento' in p:
                                player_dict['Año'] = p['año_nacimiento']
                            if 'edad' in p:
                                player_dict['Edad'] = p['edad']
                            if 'Nacionalidad' in p:
                                player_dict['Nacionalidad'] = p['Nacionalidad']
                            lista_jugadores.append(player_dict)
                
                df_export = pd.DataFrame(lista_jugadores)
                csv = df_export.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="top_jugadores_{liga_seleccionada.replace(" ", "_")}.csv">📥 Descargar CSV</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("✅ Lista CSV generada!")
        
        st.metric("👥 Jugadores Seleccionados", total_selected)
    else:
        st.info("👈 Selecciona jugadores en el panel izquierdo para ver la formación")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>⚽ Scout App 2025 | Powered by Streamlit + mplsoccer</p>
    <p>💡 Sistema de selección manual - Tú decides la posición</p>
</div>
""", unsafe_allow_html=True)