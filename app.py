import streamlit as st
import polars as pl
import altair as alt
import io

# Librerías UI
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Conciliación de Stock", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILOS VISUALES (CLARO, PASTEL Y AZUL) ---
def aplicar_estilos():
    st.markdown("""
        <style>
        /* 1. Importación de tipografías modernas (Poppins e Inter) */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Poppins:wght@500;600;700;800&display=swap');

        :root {
            --bg-base: #F0F4F8;          
            --bg-surface: #FFFFFF;       
            --bg-surface-hover: #F0F9FF; 
            --accent-primary: #3B82F6;   
            --accent-secondary: #93C5FD; 
            --text-primary: #1E293B;     
            --text-secondary: #64748B;   
            --border-color: #E2E8F0;     
            
            --shadow-soft: 0 10px 30px rgba(0, 0, 0, 0.04);
            --shadow-glow: 0 4px 15px rgba(59, 130, 246, 0.15);
            --radius-md: 8px;
            --radius-lg: 12px;
            --transition-smooth: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        header {visibility: hidden !important;}
        footer {visibility: hidden !important;}

        /* CORRECCIÓN: Quitamos [class*="st-"] y span para no romper íconos internos */
        html, body, p, label {
            font-family: 'Inter', sans-serif !important;
            line-height: 1.6 !important;
            color: var(--text-primary) !important;
        }

        .stApp { background-color: var(--bg-base) !important; }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Poppins', sans-serif !important;
            letter-spacing: -0.02em !important;
            color: var(--accent-primary) !important;
            font-weight: 600 !important;
        }

        .titulo-principal {
            font-size: clamp(2rem, 4vw, 3.2rem) !important;
            text-align: center;
            margin-bottom: clamp(1.5rem, 3vw, 2.5rem);
            color: var(--text-primary) !important;
            font-family: 'Poppins', sans-serif !important;
            font-weight: 800 !important;
            letter-spacing: -0.03em !important;
        }
        
        .titulo-principal span { color: var(--accent-primary); }

        .block-container {
            background-color: var(--bg-surface) !important;
            border-radius: var(--radius-lg) !important;
            padding: clamp(2rem, 5vw, 4rem) !important;
            max-width: 1000px !important; 
            margin: 2rem auto !important;
            border: 1px solid var(--border-color) !important;
            box-shadow: var(--shadow-soft) !important;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        div[data-testid="stHorizontalBlock"] { gap: 1.5rem !important; align-items: center !important; }

        /* CORRECCIÓN: Dejamos que Streamlit maneje el padding y el display interno */
        [data-testid="stFileUploadDropzone"] {
            background-color: #FAFAFA !important;
            border: 1.5px dashed var(--accent-secondary) !important;
            border-radius: var(--radius-md) !important;
            transition: var(--transition-smooth) !important;
        }
        
        [data-testid="stFileUploadDropzone"]:hover {
            border-color: var(--accent-primary) !important;
            background-color: var(--bg-surface-hover) !important;
        }

        button[kind="secondary"] {
            background-color: var(--bg-surface) !important;
            color: var(--accent-primary) !important;
            border: 1px solid var(--accent-secondary) !important;
            border-radius: var(--radius-md) !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            transition: var(--transition-smooth) !important;
            padding: 0.5rem 1.5rem !important;
        }

        button[kind="secondary"]:hover {
            background-color: var(--bg-surface-hover) !important;
            color: var(--accent-primary) !important;
            border-color: var(--accent-primary) !important;
            box-shadow: var(--shadow-glow) !important;
        }

        button[kind="primary"], .stButton > button {
            background-color: var(--accent-primary) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: var(--radius-md) !important;
            font-family: 'Poppins', sans-serif !important;
            font-weight: 600 !important;
            letter-spacing: 0.02em !important;
            padding: 0.75rem 2rem !important;
            width: 100% !important;
            transition: var(--transition-smooth) !important;
            box-shadow: var(--shadow-glow) !important;
        }
        
        button[kind="primary"]:hover, .stButton > button:hover {
            background-color: #2563EB !important;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3) !important;
        }

        .stDownloadButton > button {
            background-color: transparent !important;
            color: var(--accent-primary) !important;
            border: 1px solid var(--accent-primary) !important;
            border-radius: var(--radius-md) !important;
            width: 100% !important;
            transition: var(--transition-smooth) !important;
            font-family: 'Poppins', sans-serif !important;
            font-weight: 500 !important;
        }
        
        .stDownloadButton > button:hover {
            background-color: var(--bg-surface-hover) !important;
            color: var(--accent-primary) !important;
            box-shadow: var(--shadow-glow) !important;
        }

        /* --- ESTILOS DE TARJETAS DE MÉTRICAS --- */
        div[data-testid="stMetric"] {
            background-color: var(--bg-surface) !important; 
            border-radius: var(--radius-md) !important;
            padding: 1.5rem 1rem !important;
            border: 1px solid var(--border-color) !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important; 
            transition: var(--transition-smooth) !important;
            display: flex;
            flex-direction: column;
            align-items: center; 
            justify-content: center;
            text-align: center;
        }
        
        div[data-testid="stMetric"]:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 25px rgba(0, 0, 0, 0.1) !important; 
            border-color: var(--accent-secondary) !important;
        }

        div[data-testid="stMetricValue"] {
            color: var(--text-primary) !important; 
            font-family: 'Poppins', sans-serif !important;
            font-weight: 700 !important;
            font-size: clamp(1.8rem, 3vw, 2.5rem) !important;
            margin-top: 0.5rem;
        }
        
        div[data-testid="stMetricLabel"] {
            color: var(--text-secondary) !important;
            font-weight: 600 !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 1rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

aplicar_estilos()

# --- FUNCIONES AUXILIARES ---
def generar_excel(df: pl.DataFrame) -> bytes:
    output = io.BytesIO()
    df.write_excel(output)
    return output.getvalue()

def leer_archivo(uploaded_file, skip_rows=0):
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pl.read_csv(uploaded_file, has_header=False, infer_schema_length=10000, truncate_ragged_lines=True, ignore_errors=True)
        else:
            df = pl.read_excel(uploaded_file.read(), has_header=False)
        
        if skip_rows > 0:
            df = df[skip_rows:]
        return df
    except Exception as e:
        st.error(f"Error leyendo el archivo {uploaded_file.name}: {e}")
        return None

# --- ESTADO DE SESIÓN (SESSION STATE) ---
if "df_final" not in st.session_state:
    st.session_state.df_final = None
if "df_falsos" not in st.session_state:
    st.session_state.df_falsos = None
if "metricas" not in st.session_state:
    st.session_state.metricas = {}

# --- INTERFAZ GRÁFICA ---
st.markdown('<div class="titulo-principal">Conciliación de <span>Stock</span></div>', unsafe_allow_html=True)

# Subida de archivos
col_cube, col_ifs = st.columns(2)
with col_cube:
    file_cube = st.file_uploader("Archivo CUBE CAT", type=["xlsx", "csv"], help="Se ignorarán las primeras 4 filas de formato.")
with col_ifs:
    file_ifs = st.file_uploader("Archivo IFS CAT", type=["xlsx", "csv"], help="Se ignorará la primera fila de formato.")

# --- LÓGICA DE PROCESAMIENTO ---
if file_cube and file_ifs:
    if st.button("Procesar y Cruzar Datos", use_container_width=True):
        try:
            with st.spinner("Procesando y limpiando datos..."):
                
                # --- PROCESAMIENTO CUBE ---
                df_cube = leer_archivo(file_cube, skip_rows=4)
                if df_cube is not None:
                    c_cols = df_cube.columns
                    df_cube = df_cube.select([
                        pl.col(c_cols[0]).cast(pl.Utf8).str.strip_chars().alias("Articulo"),    
                        pl.col(c_cols[1]).cast(pl.Utf8).alias("Descripcion"),                  
                        pl.col(c_cols[2]).cast(pl.Float64).fill_null(0).cast(pl.Int64).alias("Stock CUBE")     
                    ]).filter(pl.col("Articulo").is_not_null() & (pl.col("Articulo") != ""))

                # --- PROCESAMIENTO IFS ---
                df_ifs = leer_archivo(file_ifs, skip_rows=1)
                if df_ifs is not None:
                    i_cols = df_ifs.columns
                    
                    if len(i_cols) < 40:
                        st.error("El archivo IFS no parece tener la estructura correcta (requiere al menos 40 columnas).")
                        st.stop()

                    df_ifs = df_ifs.select([
                        pl.col(i_cols[5]).cast(pl.Utf8).str.strip_chars().alias("Articulo"),
                        pl.col(i_cols[3]).cast(pl.Utf8).str.to_lowercase().str.strip_chars().alias("Tipo_Ubicacion"),
                        pl.col(i_cols[4]).cast(pl.Utf8).str.to_lowercase().str.strip_chars().alias("N_Ubicacion"),
                        pl.col(i_cols[38]).cast(pl.Utf8).str.strip_chars().alias("Control_Disp"),
                        pl.col(i_cols[9]).cast(pl.Float64).fill_null(0).cast(pl.Int64).alias("Cantidad")
                    ]).filter(pl.col("Articulo").is_not_null() & (pl.col("Articulo") != ""))

                    df_ifs_filtered = df_ifs.filter(
                        pl.col("Tipo_Ubicacion").is_in(["envio", "recogida", "envío"]) 
                    ).filter(
                        ~pl.col("N_Ubicacion").is_in(["averia no vendible", "averia vendible", "calidad", "cuarentena", "etiquetado", "invg", "avería no vendible", "avería vendible"])
                    ).filter(
                        pl.col("Control_Disp").is_null() | (pl.col("Control_Disp") == "") | (pl.col("Control_Disp") == "null")
                    )

                    df_ifs_grouped = df_ifs_filtered.group_by("Articulo").agg(
                        pl.col("Cantidad").sum().alias("Stock IFS")
                    )

                # --- CRUCE DE DATOS ---
                df_final = df_cube.join(df_ifs_grouped, on="Articulo", how="left")
                df_final = df_final.with_columns(
                    pl.col("Stock IFS").fill_null(0)
                ).with_columns(
                    (pl.col("Stock CUBE") - pl.col("Stock IFS")).alias("Diferencia") 
                ).with_columns(
                    (pl.col("Diferencia") == 0).alias("Verificacion")
                )

                # --- ARCHIVO DE FALSOS ---
                df_falsos = df_final.filter(~pl.col("Verificacion")).select([
                    pl.col("Articulo").alias("ITEMCODE"),
                    pl.col("Stock IFS").alias("QUANTITY")
                ])

                # Guardamos en Session State para evitar recargas
                st.session_state.df_final = df_final
                st.session_state.df_falsos = df_falsos
                st.session_state.metricas = {
                    "total": df_final.height,
                    "mismatches": df_falsos.height,
                    "matches": df_final.height - df_falsos.height,
                    "desfase_unidades": df_final.select(pl.col("Diferencia").sum()).item()
                }

        except Exception as e:
            st.error(f"Ocurrió un error procesando los datos: {e}")

# --- RENDERIZADO DE RESULTADOS ---
if st.session_state.df_final is not None:
    df_final = st.session_state.df_final
    df_falsos = st.session_state.df_falsos
    mets = st.session_state.metricas

    # --- MÉTRICAS ---
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Total CUBE", mets["total"])
    col_m2.metric("Coinciden", mets["matches"])
    col_m3.metric("Discrepancias", mets["mismatches"])
    col_m4.metric("Diferencia Unidades", mets["desfase_unidades"])
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- VISUALIZACIÓN ---
    st.markdown("### Resumen de Verificación")
    chart_data = pl.DataFrame({"Estado": ["Coinciden", "No Coinciden"], "Cantidad": [mets["matches"], mets["mismatches"]]})
    
    grafico = alt.Chart(chart_data.to_pandas()).mark_arc(innerRadius=60).encode(
        theta="Cantidad:Q",
        color=alt.Color("Estado:N", scale=alt.Scale(domain=["Coinciden", "No Coinciden"], range=["#93C5FD", "#3B82F6"])), 
        tooltip=["Estado", "Cantidad"]
    ).properties(height=350).configure_view(strokeWidth=0).configure(background='transparent')\
    .configure_legend(labelColor='#1E293B', titleColor='#1E293B', labelFont='Inter', titleFont='Poppins') 
    
    st.altair_chart(grafico, use_container_width=True)

    # --- TABLA INTERACTIVA CON FILTROS ---
    st.markdown("### Tabla de Resultados")
    
    ver_solo_errores = st.toggle("🔍 Mostrar únicamente discrepancias")
    df_mostrar = df_final.filter(~pl.col("Verificacion")) if ver_solo_errores else df_final

    gb = GridOptionsBuilder.from_dataframe(df_mostrar.to_pandas())
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_default_column(filter=True)
    
    jscode_diferencia = JsCode("""
    function(params) {
        if (params.value > 0) return {'color': '#991B1B', 'backgroundColor': '#FEE2E2'};
        if (params.value < 0) return {'color': '#92400E', 'backgroundColor': '#FEF3C7'};
        return null;
    }
    """)
    gb.configure_column("Diferencia", cellStyle=jscode_diferencia)

    gb.configure_column("Verificacion", 
                        cellStyle= {
                            "color": "#FFFFFF",
                            "backgroundColor": "#3B82F6", 
                            "borderRadius": "4px",
                            "fontWeight": "600",
                            "fontFamily": "Inter"
                        })
    gridOptions = gb.build()
    
    AgGrid(
        df_mostrar.to_pandas(), 
        gridOptions=gridOptions, 
        height=400, 
        fit_columns_on_grid_load=True, 
        theme='balham',
        allow_unsafe_jscode=True
    )

    # --- DESCARGAS ---
    st.markdown("<h3 style='text-align: center; margin-top: 1rem; margin-bottom: 1.5rem;'>Descargar Resultados</h3>", unsafe_allow_html=True)
    
    _, col_centro, _ = st.columns([1, 2, 1])
    
    with col_centro:
        col_btn1, col_btn2 = st.columns(2)
        
        excel_completo = generar_excel(df_final)
        excel_falsos = generar_excel(df_falsos)

        with col_btn1:
            st.download_button(
                label="Descargar Cruce Completo",
                data=excel_completo,
                file_name="Cruce_Stocks_Completo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
                
        with col_btn2:
            st.download_button(
                label="Descargar Carga a CUBE",
                data=excel_falsos,
                file_name="Mismatches_IFS.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
