import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from io import BytesIO

st.set_page_config(page_title="Dashboard Proyectivo - Vespasiani", layout="wide")

@st.cache_data
def load_data():
    archivo = "reporte_repuestos_mostrador.xlsx"
    df = pd.read_excel(archivo, sheet_name="MOSTRADOR", skiprows=1)
    df.columns = df.columns.str.strip()
    df['fecha'] = pd.to_datetime(df['fecha'])
    cols_num = ["Costo Total", "Venta Total", "Utilidad", "(%) Utilidad"]
    for col in cols_num:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

try:
    df = load_data()

    # --- BARRA LATERAL ---
    st.sidebar.header("🎯 Filtros y Control")
    meses_disponibles = df["Mes"].unique()
    filtro_meses = st.sidebar.multiselect("Meses", meses_disponibles, default=meses_disponibles)
    filtro_sucursal = st.sidebar.multiselect("Sucursal", df["Sucursal"].unique(), default=df["Sucursal"].unique())
    
    mask = df["Mes"].isin(filtro_meses) & df["Sucursal"].isin(filtro_sucursal)
    df_f = df[mask]

    st.title("📈 Análisis de Performance y Proyecciones")

    # --- SECCIÓN DE PROYECCIONES ---
    st.subheader("🔮 Tendencia y Proyección de Facturación")
    
    # Agrupamos por mes para la serie temporal
    # Usamos Año y Mes para que el orden sea correcto
    df_proy = df_f.groupby(['Año', 'Mes']).agg({'Venta Total': 'sum'}).reset_index()
    
    # Crear un índice numérico para calcular la tendencia (regresión simple)
    df_proy['n_mes'] = range(len(df_proy))
    
    if len(df_proy) > 1:
        # Cálculo de la línea de tendencia (y = mx + b)
        z = np.polyfit(df_proy['n_mes'], df_proy['Venta Total'], 1)
        p = np.poly1d(z)
        df_proy['Tendencia'] = p(df_proy['n_mes'])

        # Crear gráfico de proyección
        fig_proy = go.Figure()

        # Línea de Ventas Reales
        fig_proy.add_trace(go.Scatter(
            x=df_proy['Mes'], y=df_proy['Venta Total'],
            mode='lines+markers', name='Venta Real',
            line=dict(color='#0083B8', width=4)
        ))

        # Línea de Proyección/Tendencia
        fig_proy.add_trace(go.Scatter(
            x=df_proy['Mes'], y=df_proy['Tendencia'],
            mode='lines', name='Tendencia (Proyección)',
            line=dict(color='red', width=2, dash='dash')
        ))

        fig_proy.update_layout(
            title="Evolución Mensual con Línea de Tendencia",
            xaxis_title="Meses",
            yaxis_title="Monto Facturado",
            template="plotly_white",
            hovermode="x unified"
        )
        st.plotly_chart(fig_proy, use_container_width=True)
        
        # Mensaje de Insight
        crecimiento = z[0]
        if crecimiento > 0:
            st.success(f"📈 La tendencia actual indica un **crecimiento promedio de $ {crecimiento:,.0f}** por mes.")
        else:
            st.warning(f"📉 La tendencia actual indica una **baja promedio de $ {abs(crecimiento):,.0f}** por mes.")
    else:
        st.info("Selecciona más meses para poder calcular una proyección.")

    st.markdown("---")

    # --- RANKINGS DE CLIENTES Y VENDEDORES ---
    col_v, col_c = st.columns(2)

    with col_v:
        st.subheader("🏆 Top Vendedores (Rentabilidad)")
        ranking_v = df_f.groupby("Corredor").agg({"Venta Total": "sum", "Utilidad": "sum"}).sort_values("Utilidad", ascending=False).reset_index()
        st.dataframe(ranking_v.style.format({"Venta Total": "$ {:,.0f}", "Utilidad": "$ {:,.0f}"}), use_container_width=True)

    with col_c:
        st.subheader("👤 Clientes con Mayor Facturación")
        ranking_c = df_f.groupby("cliente").agg({"Venta Total": "sum", "Utilidad": "sum"}).sort_values("Venta Total", ascending=False).reset_index()
        st.dataframe(ranking_c.head(10).style.format({"Venta Total": "$ {:,.0f}", "Utilidad": "$ {:,.0f}"}), use_container_width=True)

    # --- EXPORTACIÓN ---
    st.markdown("---")
    def to_excel(df_exp):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_exp.to_excel(writer, index=False, sheet_name='Datos')
        return output.getvalue()

    st.download_button("📥 Descargar Datos en Excel", data=to_excel(df_f), file_name="reporte_vespasiani.xlsx")

except Exception as e:
    st.error(f"Error: {e}")
