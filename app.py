import streamlit as st

# Verificación de librerías para evitar el error de importación
try:
    import pandas as pd
    import plotly.express as px
except ModuleNotFoundError as e:
    st.error(f"Error: No se encontró la librería '{e.name}'. Asegúrate de que esté en requirements.txt")
    st.stop()

# Configuración de la página
st.set_page_config(page_title="Dashboard de Repuestos", layout="wide")

@st.cache_data
def load_data():
    # Saltamos la primera fila para obtener los encabezados correctos del Excel
    df = pd.read_excel("reporte_repuestos_mostrador.xlsx", sheet_name="MOSTRADOR", skiprows=1)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
    st.title("📊 Control de Gestión - Repuestos")
    
    # Filtros
    sucursal = st.sidebar.multiselect("Sucursal", df["Sucursal"].unique(), default=df["Sucursal"].unique())
    df_filt = df[df["Sucursal"].isin(sucursal)]

    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("Ventas Totales", f"$ {df_filt['Venta Total'].sum():,.0f}")
    c2.metric("Utilidad Media", f"{df_filt['(%) Utilidad'].mean():.2f}%")
    c3.metric("Operaciones", len(df_filt))

    # Gráfico de Ventas
    fig = px.bar(df_filt.groupby("Grupo")[["Venta Total"]].sum().reset_index(), 
                 x="Grupo", y="Venta Total", title="Ventas por Marca")
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Hubo un problema al leer los datos: {e}")
