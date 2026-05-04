import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard de Repuestos", layout="wide")

# Función para cargar datos
@st.cache_data
def load_data():
    # Cargamos el archivo saltando la primera fila de título para que los encabezados sean correctos
    df = pd.read_excel("reporte_repuestos_mostrador.xlsx", sheet_name="MOSTRADOR", skiprows=1)
    
    # Convertir fecha a formato datetime
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    # Limpiar nombres de columnas por si tienen espacios
    df.columns = df.columns.str.strip()
    
    return df

# Intentar cargar los datos
try:
    df = load_data()

    st.title("📊 KPI de Facturación - Repuestos Mostrador")
    st.markdown("---")

    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header("Filtros")
    sucursales = st.sidebar.multiselect(
        "Seleccionar Sucursal:",
        options=df["Sucursal"].unique(),
        default=df["Sucursal"].unique()
    )

    marcas = st.sidebar.multiselect(
        "Seleccionar Marca (Grupo):",
        options=df["Grupo"].unique(),
        default=df["Grupo"].unique()
    )

    # Aplicar filtros
    df_selection = df.query("Sucursal == @sucursales & Grupo == @marcas")

    # --- INDICADORES PRINCIPALES (KPIs) ---
    total_ventas = df_selection["Venta Total"].sum()
    utilidad_promedio = df_selection["(%) Utilidad"].mean()
    total_operaciones = df_selection.shape[0]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Ventas Totales", f"$ {total_ventas:,.2f}")
    with col2:
        st.metric("Margen Promedio", f"{utilidad_promedio:.2f}%")
    with col3:
        st.metric("Cant. Operaciones", total_operaciones)

    st.markdown("---")

    # --- GRÁFICOS ---
    col_left, col_right = st.columns(2)

    # Gráfico 1: Ventas por Marca
    ventas_grupo = df_selection.groupby("Grupo")[["Venta Total"]].sum().reset_index()
    fig_grupo = px.bar(
        ventas_grupo,
        x="Grupo",
        y="Venta Total",
        title="<b>Ventas por Marca</b>",
        color_discrete_sequence=["#0083B8"],
        template="plotly_white",
    )
    col_left.plotly_chart(fig_grupo, use_container_width=True)

    # Gráfico 2: Ventas por Mes
    ventas_mes = df_selection.groupby("Mes")[["Venta Total"]].sum().reindex(
        ['Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo']
    ).reset_index()
    
    fig_mes = px.line(
        ventas_mes,
        x="Mes",
        y="Venta Total",
        title="<b>Tendencia Mensual</b>",
        markers=True,
        template="plotly_white",
    )
    col_right.plotly_chart(fig_mes, use_container_width=True)

    # Mostrar tabla de datos al final
    with st.expander("Ver detalle de datos filtrados"):
        st.dataframe(df_selection)

except Exception as e:
    st.error(f"Error al cargar el archivo: {e}")
    st.info("Asegúrate de que el archivo 'reporte_repuestos_mostrador.xlsx' esté en la misma carpeta que este código.")
