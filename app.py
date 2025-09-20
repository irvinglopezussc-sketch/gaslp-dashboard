import streamlit as st
import pandas as pd
import altair as alt
from datetime import date

# --- Inicialización de datos ---
if "ventas" not in st.session_state:
    st.session_state.ventas = []

st.set_page_config(page_title="Control de Ventas Gas LP", layout="wide")

# --- Título ---
st.title("📊 Control de Ventas de Gas LP")

# --- Configuración de metas ---
st.sidebar.header("⚙️ Configuración")
meta_mensual = st.sidebar.number_input("Meta mensual (Lts)", min_value=0, value=30000, step=1000)
dias_habiles = st.sidebar.number_input("Días hábiles del mes", min_value=1, max_value=31, value=25)

# --- Registro de ventas ---
st.subheader("➕ Registrar nueva venta")
with st.form("form_venta", clear_on_submit=True):
    fecha = st.date_input("Fecha", value=date.today())
    operador = st.text_input("Operador")
    region = st.text_input("Región")
    litros = st.number_input("Litros vendidos", min_value=0, step=10)
    submit = st.form_submit_button("Guardar")

    if submit:
        st.session_state.ventas.append({
            "Fecha": fecha,
            "Operador": operador,
            "Región": region,
            "Litros": litros
        })
        st.success("✅ Venta registrada correctamente")

# --- Mostrar tabla de ventas ---
df = pd.DataFrame(st.session_state.ventas)
st.subheader("📋 Ventas registradas")
st.dataframe(df)

# --- Cálculo de KPIs ---
if not df.empty:
    ventas_acum = df["Litros"].sum()
    meta_diaria = meta_mensual / dias_habiles
    dias_registrados = df["Fecha"].nunique()
    dias_restantes = max(dias_habiles - dias_registrados, 1)
    necesidad_diaria = (meta_mensual - ventas_acum) / dias_restantes

    col1, col2, col3 = st.columns(3)
    col1.metric("Meta mensual", f"{meta_mensual:,} Lts")
    col2.metric("Venta acumulada", f"{ventas_acum:,} Lts")
    col3.metric("% Cumplimiento", f"{ventas_acum/meta_mensual:.1%}")

    col4, col5 = st.columns(2)
    col4.metric("Meta diaria", f"{meta_diaria:,.0f} Lts")
    col5.metric("Necesidad diaria restante", f"{necesidad_diaria:,.0f} Lts")

    # --- Gráficas ---
    st.subheader("📈 Avance de Ventas vs Meta")

    # Agrupar ventas por fecha
    df_grouped = df.groupby("Fecha")["Litros"].sum().reset_index()
    df_grouped["Acumulado"] = df_grouped["Litros"].cumsum()

    # Serie de meta acumulada
    df_grouped["Meta acumulada"] = [(i+1)*meta_diaria for i in range(len(df_grouped))]

    # Gráfica de barras (ventas diarias)
    bar_chart = alt.Chart(df_grouped).mark_bar(color="#1f77b4").encode(
        x="Fecha:T",
        y="Litros:Q",
        tooltip=["Fecha", "Litros"]
    ).properties(title="Ventas diarias")

    # Gráfica de líneas (acumulado vs meta)
    line_chart = alt.Chart(df_grouped).mark_line(point=True).encode(
        x="Fecha:T",
        y="Acumulado:Q",
        color=alt.value("green"),
        tooltip=["Fecha", "Acumulado"]
    )

    meta_line = alt.Chart(df_grouped).mark_line(strokeDash=[5,5], color="red").encode(
        x="Fecha:T",
        y="Meta acumulada:Q",
        tooltip=["Fecha", "Meta acumulada"]
    )

    # Mostrar gráficas
    st.altair_chart(bar_chart, use_container_width=True)
    st.altair_chart(line_chart + meta_line, use_container_width=True)
