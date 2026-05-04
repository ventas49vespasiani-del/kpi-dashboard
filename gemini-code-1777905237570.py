import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# 1. Configuración y Estilo
st.set_page_config(page_title="Gestión de Repuestos - Vespasiani", layout="wide")

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

    # --- BARRA LATERAL: FILTROS ---
    st.sidebar.header("🎯 Filtros de Control")
    
    # Filtro de Meses (Ordenados cronológicamente si es posible)
    meses_disponibles = df["Mes"].unique()
    filtro_meses = st.sidebar.multiselect("Seleccionar Meses", meses_disponibles, default=meses_disponibles)
    
    filtro_sucursal = st.sidebar.multiselect("Sucursal", df["Sucursal"].unique(), default=df["Sucursal"].unique())
    filtro_vendedor = st.sidebar.multiselect("Vendedor", df["Corredor"].unique(), default=df["Corredor"].unique())

    # Aplicar filtros
    mask = df["Mes"].isin(filtro_meses) & df["Sucursal"].isin(filtro_sucursal) & df["Corredor"].isin(filtro_vendedor)
    df_f = df[mask]

    # --- TÍTULOS ---
    st.title("🚀 Dashboard de Performance: Repuestos Mostrador")
    
    # --- RESUMEN GLOBAL ---
    st.subheader("📋 Resumen Ejecutivo Global")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Venta Total", f"$ {df_f['Venta Total'].sum():,.0f}")
    c2.metric("Utilidad Bruta", f"$ {df_f['Utilidad'].sum():,.0f}")
    c3.metric("Margen Promedio", f"{df_f['(%) Utilidad'].mean():.2f}%")
    c4.metric("Operaciones", f"{len(df_f)}")

    st.markdown("---")

    # --- ANÁLISIS DE RANKINGS (VENDEDORES Y CLIENTES) ---
    col_v, col_c = st.columns(2)

    with col_v:
        st.subheader("🏆 Top Vendedores")
        # Agrupamos para ver Facturación y Rentabilidad por Vendedor
        ranking_v = df_f.groupby("Corredor").agg({
            "Venta Total": "sum",
            "Utilidad": "sum"
        }).sort_values("Venta Total", ascending=False).reset_index()
        
        st.dataframe(ranking_v.style.format({"Venta Total": "$ {:,.0f}", "Utilidad": "$ {:,.0f}"}), use_container_width=True)
        
        fig_v = px.bar(ranking_v.head(5), x="Venta Total", y="Corredor", orientation='h', title="Top 5 Facturación", color="Utilidad")
        st.plotly_chart(fig_v, use_container_width=True)

    with col_c:
        st.subheader("👤 Top Clientes (Facturación y Rentabilidad)")
        # Agrupamos por Cliente
        ranking_c = df_f.groupby("cliente").agg({
            "Venta Total": "sum",
            "Utilidad": "sum",
            "comprobante": "count"
        }).rename(columns={"comprobante": "Compras"}).sort_values("Venta Total", ascending=False).reset_index()
        
        st.dataframe(ranking_c.head(10).style.format({"Venta Total": "$ {:,.0f}", "Utilidad": "$ {:,.0f}"}), use_container_width=True)
        
        fig_c = px.scatter(ranking_c.head(20), x="Venta Total", y="Utilidad", size="Compras", hover_name="cliente", title="Clientes: Facturación vs Rentabilidad")
        st.plotly_chart(fig_c, use_container_width=True)

    st.markdown("---")

    # --- RESUMEN INDIVIDUAL (BÚSQUEDA) ---
    st.subheader("🔍 Análisis Individual de Cliente")
    cliente_sel = st.selectbox("Buscar un cliente específico:", ["Seleccione..."] + list(df_f["cliente"].unique()))
    
    if cliente_sel != "Seleccione...":
        df_ind = df_f[df_f["cliente"] == cliente_sel]
        ci1, ci2, ci3 = st.columns(3)
        ci1.write(f"**Total Comprado:** $ {df_ind['Venta Total'].sum():,.2f}")
        ci2.write(f"**Rentabilidad Dejada:** $ {df_ind['Utilidad'].sum():,.2f}")
        ci3.write(f"**Margen Promedio Cliente:** {df_ind['(%) Utilidad'].mean():.2f}%")
        st.table(df_ind[["fecha", "comprobante", "Venta Total", "Utilidad", "Corredor"]])

    st.markdown("---")

    # --- EXPORTAR A EXCEL ---
    st.subheader("📥 Descargar Reporte")
    
    def to_excel(df_to_download):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_to_download.to_excel(writer, index=False, sheet_name='Reporte_Filtrado')
        return output.getvalue()

    excel_data = to_excel(df_f)
    st.download_button(
        label="📥 Descargar datos filtrados en Excel",
        data=excel_data,
        file_name='reporte_personalizado_vespasiani.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

except Exception as e:
    st.error(f"Error: {e}")
