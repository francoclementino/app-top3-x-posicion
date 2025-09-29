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
    }
    .player-card {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        border-left: 4px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>⚽ SCOUT APP - EQUIPO 11 IDEAL</h1>
    <p>Selecciona tu TOP 3 por posición en cada liga</p>
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
        # Si ya es datetime, extraer año
        if isinstance(date_str, datetime):
            return date_str.year
        # Si es string, parsear
        date_obj = pd.to_datetime(date_str)
        return date_obj.year
    except:
        return None

# Simulación de datos (reemplazar con tu Excel)
@st.cache_data
def load_sample_data():
    data = {
        'Jugador': ['Jorge de Asis', 'Luciano Sábato', 'Agustín Obregon', 'Facundo Kalinger', 
                   'Santiago Zampieri', 'Gonzalo Zelarayán', 'Facundo Pimienta', 'Samuel Beltrán',
                   'Faustino Messina', 'Facundo Herrera', 'Lautaro Espeche'],
        'Posición': ['Delantero', 'Delantero', 'Lateral Derecho', 'Lateral Izquierdo',
                    'Lateral Izquierdo', 'Mediocampista', 'Mediocampista', 'Defensor Central',
                    'Defensor Central', 'Defensor Central', 'Arquero'],
        'altura': [1.78, 1.82, 1.75, 1.80, 1.77, 1.85, 1.83, 1.88, 1.90, 1.79, 1.85],
        'areaNacimiento_nombre': ['Argentina', 'Argentina', 'Argentina', 'Argentina',
                                 'Argentina', 'Argentina', 'Argentina', 'Argentina',
                                 'Argentina', 'Argentina', 'Argentina'],
        'urlImagen.y': ['https://logoeps.com/wp-content/uploads/2013/03/gimnasia-la-plata-vector-logo.png',
                       'https://logoeps.com/wp-content/uploads/2013/03/san-lorenzo-vector-logo.png',
                       'https://logoeps.com/wp-content/uploads/2013/03/river-plate-vector-logo.png',
                       'https://logoeps.com/wp-content/uploads/2013/03/huracan-vector-logo.png',
                       'https://logoeps.com/wp-content/uploads/2013/03/boca-juniors-vector-logo.png',
                       None, None, None, None, None, None],
        'liga': ['Primera División', 'Primera División', 'Primera División', 'Primera División',
                'Primera División', 'Primera División', 'Primera División', 'Primera División',
                'Primera División', 'Primera División', 'Primera División'],
        'fechaNacimiento': ['2006-03-15', '2008-07-20', '2006-01-10', '2005-11-25',
                           '2007-05-30', '2004-09-12', '2003-12-08', '2004-04-18',
                           '2006-08-22', '2006-02-14', '2004-10-03'],
        'urlImagen.x': [None, None, None, None, None, None, None, None, None, None, None]
    }
    return pd.DataFrame(data)

# Función para cargar tu Excel (descomenta cuando tengas el archivo)
def load_excel_data(uploaded_file):
    """
    Carga y procesa tu archivo Excel
    """
    df = pd.read_excel(uploaded_file)
    
    # Procesar fechas de nacimiento para extraer año
    df['año_nacimiento'] = df['fechaNacimiento'].apply(extract_year_from_date)
    
    # Calcular edad
    current_year = datetime.now().year
    df['edad'] = current_year - df['año_nacimiento']
    
    return df

# Cargar datos
st.sidebar.header("📁 CARGAR DATOS")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo Excel", type=['xlsx', 'xls'])

if uploaded_file is not None:
    try:
        df = load_excel_data(uploaded_file)
        st.sidebar.success("✅ Archivo cargado correctamente!")
    except Exception as e:
        st.sidebar.error(f"❌ Error al cargar archivo: {e}")
        df = load_sample_data()  # Usar datos de ejemplo
else:
    st.sidebar.info("📝 Usando datos de ejemplo")
    df = load_sample_data()
    # Procesar datos de ejemplo
    df['año_nacimiento'] = df['fechaNacimiento'].apply(extract_year_from_date)
    df['edad'] = datetime.now().year - df['año_nacimiento']

# Sidebar con filtros
st.sidebar.markdown('<div class="filter-box">', unsafe_allow_html=True)
st.sidebar.header("🔍 FILTROS")

# Filtros
ligas_disponibles = df['liga'].unique()
liga_seleccionada = st.sidebar.selectbox("📊 Seleccionar Liga:", ligas_disponibles)

# Filtrar por liga primero
df_liga = df[df['liga'] == liga_seleccionada]

# Filtro por nacionalidad
nacionalidades = df_liga['areaNacimiento_nombre'].unique()
nacionalidades_seleccionadas = st.sidebar.multiselect(
    "🌍 Nacionalidades:", 
    nacionalidades, 
    default=nacionalidades
)

# Sin filtros de altura ni edad por ahora

st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Aplicar filtros (sin altura ni edad)
df_filtrado = df_liga[
    (df_liga['areaNacimiento_nombre'].isin(nacionalidades_seleccionadas))
]

# Función para obtener TOP 3 por posición (simulando ranking por año nacimiento)
def get_top3_by_position(df, position):
    pos_players = df[df['Posición'] == position]
    if len(pos_players) == 0:
        return pd.DataFrame()
    
    # Ordenar por año nacimiento (más jóvenes primero) como criterio de ejemplo
    # Puedes cambiar esto por cualquier métrica que tengas
    top3 = pos_players.nsmallest(3, 'año_nacimiento')
    return top3

# Función para crear la cancha con jugadores
def create_pitch_with_players(top_players_dict):
    # Crear la cancha
    fig, ax = plt.subplots(figsize=(16, 11))
    pitch = Pitch(
        pitch_type='opta',
        pitch_color='#2d8f2d',
        line_color='white',
        linewidth=3
    )
    pitch.draw(ax=ax)
    
    # Posiciones en la cancha (coordenadas Opta: 0-100 x, 0-100 y)
    positions = {
        'Arquero': [(10, 50)],
        'Defensor Central': [(25, 35), (25, 50), (25, 65)],
        'Lateral Izquierdo': [(25, 15)],
        'Lateral Derecho': [(25, 85)],
        'Mediocampista': [(50, 30), (50, 50), (50, 70)],
        'Delantero': [(80, 35), (80, 50), (80, 65)]
    }
    
    # Colores por posición
    colors = {
        'Arquero': '#FFD700',
        'Defensor Central': '#4169E1',
        'Lateral Izquierdo': '#4169E1',
        'Lateral Derecho': '#4169E1',
        'Mediocampista': '#32CD32',
        'Delantero': '#FF4500'
    }
    
    # Agregar jugadores a la cancha
    for position, coords in positions.items():
        if position in top_players_dict:
            players = top_players_dict[position]
            for i, (x, y) in enumerate(coords[:len(players)]):
                if i < len(players):
                    player = players.iloc[i]
                    
                    # Círculo para el jugador
                    circle = plt.Circle((x, y), 4, 
                                      color=colors[position], 
                                      alpha=0.9, 
                                      zorder=10,
                                      edgecolor='white',
                                      linewidth=2)
                    ax.add_patch(circle)
                    
                    # Nombre del jugador
                    ax.text(x, y-9, f"{player['Jugador']}", 
                           ha='center', va='top', 
                           fontsize=9, fontweight='bold',
                           color='white',
                           bbox=dict(boxstyle="round,pad=0.3", 
                                   facecolor='black', 
                                   alpha=0.8))
                    
                    # Año, altura y edad
                    info_text = f"({player['año_nacimiento']}) - {player['altura']}m - {player['edad']} años"
                    ax.text(x, y+9, info_text, 
                           ha='center', va='bottom',
                           fontsize=8,
                           color='white',
                           bbox=dict(boxstyle="round,pad=0.2", 
                                   facecolor=colors[position], 
                                   alpha=0.9))
                    
                    # Logo del equipo (si existe)
                    if not pd.isna(player['urlImagen.y']) and player['urlImagen.y'] != '':
                        try:
                            logo_img = load_image_from_url(player['urlImagen.y'], size=(25, 25))
                            if logo_img:
                                # Convertir PIL a array para matplotlib
                                import numpy as np
                                logo_array = np.array(logo_img)
                                imagebox = OffsetImage(logo_array, zoom=0.5)
                                ab = AnnotationBbox(imagebox, (x+6, y+6), frameon=False)
                                ax.add_artist(ab)
                        except:
                            pass  # Si falla cargar logo, continúa sin él
    
    # Título
    ax.text(50, 108, f"EQUIPO 11 IDEAL", 
           ha='center', va='bottom',
           fontsize=18, fontweight='bold',
           color='white')
    
    ax.text(50, 104, f"{liga_seleccionada.upper()}", 
           ha='center', va='bottom',
           fontsize=14, fontweight='bold',
           color='white')
    
    # Fecha
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
    st.subheader("📋 TOP 3 POR POSICIÓN")
    
    posiciones = ['Arquero', 'Defensor Central', 'Lateral Izquierdo', 
                 'Lateral Derecho', 'Mediocampista', 'Delantero']
    
    top_players_dict = {}
    
    for posicion in posiciones:
        with st.expander(f"⚽ {posicion}", expanded=True):
            top3 = get_top3_by_position(df_filtrado, posicion)
            if not top3.empty:
                top_players_dict[posicion] = top3
                for idx, player in top3.iterrows():
                    st.markdown(f"""
                    <div class="player-card">
                        <strong>{player['Jugador']}</strong> ({player['año_nacimiento']}) - {player['edad']} años
                        <br>📏 {player['altura']}m | 🌍 {player['areaNacimiento_nombre']}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No hay jugadores disponibles")

with col2:
    st.subheader("🏟️ CANCHA INTERACTIVA")
    
    if top_players_dict:
        # Crear y mostrar la cancha
        fig = create_pitch_with_players(top_players_dict)
        st.pyplot(fig)
        
        # Botón para exportar
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            if st.button("📄 EXPORTAR PNG", type="primary"):
                # Convertir matplotlib a imagen
                img_buffer = io.BytesIO()
                fig.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight',
                           facecolor='#2d8f2d', edgecolor='none')
                img_buffer.seek(0)
                
                # Crear enlace de descarga
                b64 = base64.b64encode(img_buffer.getvalue()).decode()
                href = f'<a href="data:image/png;base64,{b64}" download="equipo_11_ideal_{liga_seleccionada.replace(" ", "_")}.png">📥 Descargar PNG</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("✅ Imagen PNG generada!")
        
        with col_export2:
            if st.button("📋 EXPORTAR LISTA"):
                # Crear lista de jugadores seleccionados
                lista_jugadores = []
                for pos, players in top_players_dict.items():
                    for idx, player in players.iterrows():
                        lista_jugadores.append({
                            'Posición': pos,
                            'Jugador': player['Jugador'],
                            'Año': player['año_nacimiento'],
                            'Altura': player['altura'],
                            'Nacionalidad': player['areaNacimiento_nombre']
                        })
                
                df_export = pd.DataFrame(lista_jugadores)
                csv = df_export.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="top_jugadores_{liga_seleccionada.replace(" ", "_")}.csv">📥 Descargar CSV</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("✅ Lista CSV generada!")
    else:
        st.info("🔍 Ajusta los filtros para ver jugadores disponibles")

# Estadísticas generales
st.markdown("---")
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

with col_stat1:
    st.metric("👥 Jugadores Filtrados", len(df_filtrado))

with col_stat2:
    st.metric("🌍 Nacionalidades", len(df_filtrado['areaNacimiento_nombre'].unique()))

with col_stat3:
    if not df_filtrado.empty:
        st.metric("📏 Altura Promedio", f"{df_filtrado['altura'].mean():.2f}m")

with col_stat4:
    if not df_filtrado.empty:
        st.metric("🎂 Edad Promedio", f"{df_filtrado['edad'].mean():.1f} años")

# Vista previa de datos
with st.expander("👀 Vista Previa de Datos"):
    if not df_filtrado.empty:
        st.dataframe(
            df_filtrado[['Jugador', 'Posición', 'altura', 'areaNacimiento_nombre', 'año_nacimiento', 'edad']],
            use_container_width=True
        )
    else:
        st.info("No hay datos para mostrar con los filtros actuales")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>⚽ Scout App 2025 | Powered by Streamlit + mplsoccer</p>
    <p>📁 Sube tu Excel para usar datos reales</p>
</div>
""", unsafe_allow_html=True)