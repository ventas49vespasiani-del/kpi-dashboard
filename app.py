import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de página
st.set_page_config(page_title="Dashboard Profesional - Vespasiani", layout="wide")

# 2. Función de carga de datos optimizada
@st.cache_data
def load_data():
    archivo = "reporte_repuestos_mostrador.xlsx"
    # Saltamos la primera fila de título decorativo
    df = pd.read_excel(archivo, sheet_name="MOSTRADOR", skiprows=1)
    
    # Limpieza de nombres de columnas y conversión de tipos
    df.columns = df.columns.str.strip()
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    # Asegurar que los valores sean numéricos para evitar errores en gráficos
    cols_numericas = ["Costo Total", "Venta Total", "Utilidad", "(%) Utilidad"]
    for col in cols_numericas:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df

try:
    df = load_data()

    # --- TÍTULO Y LOGO ---
    st.title("📊 Control de Gestión: Repuestos Mostrador")
    st.markdown(f"**Periodo:** {df['fecha'].min().strftime('%d/%m/%Y')} al {df['fecha'].max().strftime('%d/%m/%Y')}")
    st.markdown("---")

    # --- BARRA LATERAL: FILTROS AVANZADOS ---
    st.sidebar.header("Filtros de Análisis")
    
    filtro_sucursal = st.sidebar.multiselect("Sucursal", df["Sucursal"].unique(), default=df["Sucursal"].unique())
    filtro_vendedor = st.sidebar.multiselect("Vendedor (Corredor)", df["Corredor"].unique(), default=df["Corredor"].unique())
    filtro_tipo_cliente = st.sidebar.multiselect("Tipo de Cliente", df["Tipo Cliente"].unique(), default=df["Tipo Cliente"].unique())

    # Aplicar Filtros
    mask = df["Sucursal"].isin(filtro_sucursal) & df["Corredor"].isin(filtro_vendedor) & df["Tipo Cliente"].isin(filtro_tipo_cliente)
    df_filtrado = df[mask]

    # --- FILA 1: KPIs PRINCIPALES ---
    total_venta = df_filtrado["Venta Total"].sum()
    total_utilidad = df_filtrado["Utilidad"].sum()
    margen_promedio = df_filtrado["(%) Utilidad"].mean()
    operaciones = len(df_filtrado)

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Ventas Totales", f"$ {total_venta:,.0f}")
    kpi2.metric("Utilidad Bruta", f"$ {total_utilidad:,.0f}")
    kpi3.metric("Margen Promedio", f"{margen_promedio:.2f}%")
    kpi4.metric("N° Operaciones", operaciones)

    st.markdown("---")

    # --- FILA 2: GRÁFICOS DE DESEMPEÑO ---
    col_vendedores, col_clientes = st.columns(2)

    with col_vendedores:
        st.subheader("Top Vendedores por Facturación")
        ventas_vendedor = df_filtrado.groupby("Corredor")[["Venta Total"]].sum().reset_index().sort_values("Venta Total", ascending=True)
        fig_vendedor = px.bar(
            ventas_vendedor.tail(10), # Mostramos los 10 mejores
            y="Corredor", 
            x="Venta Total", 
            orientation='h',
            text_auto='.2s',
            color="Venta Total",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_vendedor, use_container_width=True)

    with col_clientes:
        st.subheader("Distribución por Tipo de Cliente")
        fig_pie = px.pie(
            df_filtrado, 
            values="Venta Total", 
            names="Tipo Cliente", 
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- FILA 3: ANÁLISIS MENSUAL ---
    st.subheader("Evolución Mensual de Ventas y Utilidad")
    # Agrupamos por mes y año para el gráfico de líneas
    df_mensual = df_filtrado.groupby(["Año", "Mes"])[["Venta Total", "Utilidad"]].sum().reset_index()
    # Ordenar meses cronológicamente (opcional pero recomendado)
    fig_linea = px.line(
        df_mensual, 
        x="Mes", 
        y=["Venta Total", "Utilidad"], 
        markers=True,
        title="Tendencia de Facturación vs Ganancia",
        template="plotly_white"
    )
    st.plotly_chart(fig_linea, use_container_width=True)

    # --- DETALLE DE DATOS ---
    with st.expander("🔍 Explorar datos detallados"):
        st.dataframe(df_filtrado[["fecha", "comprobante", "cliente", "Venta Total", "Utilidad", "Corredor", "Sucursal"]])

except Exception as e:
    st.error(f"Error crítico en la aplicación: {e}")
    st.info("Revisa que el archivo 'reporte_repuestos_mostrador.xlsx' tenga las columnas: Venta Total, Utilidad, Corredor, Mes, Año.")
