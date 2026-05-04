import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard de Repuestos", layout="wide")
st.title("📊 KPI de Facturación - Repuestos Mostrador")

# Leer el Excel (ajustado a tu archivo reporte_repuestos_mostrador.xlsx)
@st.cache_data
def load_data():
    df = pd.read_excel("reporte_repuestos_mostrador.xlsx", sheet_name="MOSTRADOR", skiprows=1)
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df

df = load_data()

# Filtro lateral
sucursal = st.sidebar.multiselect("Seleccionar Sucursal", options=df["Sucursal"].unique(), default=df["Sucursal"].unique())
df_selection = df.query("Sucursal == @sucursal")

# KPIs Principales
total_ventas = df_selection["Venta Total"].sum()
utilidad_media = df_selection["(%) Utilidad"].mean()

col1, col2 = st.columns(2)
with col1:
    st.metric("Ventas Totales", f"$ {total_ventas:,.2f}")
with col2:
    st.metric("Margen Utilidad Promedio", f"{utilidad_media:.2f}%")

# Gráfico de Ventas por Mes
st.subheader("Evolución de Ventas por Mes")
ventas_mensuales = df_selection.groupby(by=["Mes"]).sum(numeric_only=True)[["Venta Total"]]
fig_ventas = px.line(ventas_mensuales, x=ventas_mensuales.index, y="Venta Total", template="plotly_white")
st.plotly_chart(fig_ventas, use_container_width=True)