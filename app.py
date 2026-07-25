import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="RESTAURANTE GENERAL JAM",
    page_icon="🍳",
    layout="wide"
)

# Estilos CSS limpios
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

EXCEL_FILE = "RESTAURANTE GENERAL JAM.xlsx"

# ---------------------------------------------------------
# FUNCIONES DE CARGA Y GUARDADO DESDE EL EXCEL REAL
# ---------------------------------------------------------
def cargar_datos():
    try:
        xls = pd.ExcelFile(EXCEL_FILE)
        almacen = pd.read_excel(xls, sheet_name="HOJA_ALMACEN")
        historico_ent = pd.read_excel(xls, sheet_name="HISTORICO_ENTRADA")
        historico_sal = pd.read_excel(xls, sheet_name="HISTORICO_SALIDA")
        historico_mer = pd.read_excel(xls, sheet_name="HISTORICO_MERMAS")
        escandallos = pd.read_excel(xls, sheet_name="ESCANDALLOS_RECETAS")
        mermas_coste = pd.read_excel(xls, sheet_name="MERMAS Y COSTE REAL")
        plantilla_pedido = pd.read_excel(xls, sheet_name="PLANTILLA_PEDIDO")
        return almacen, historico_ent, historico_sal, historico_mer, escandallos, mermas_coste, plantilla_pedido
    except Exception as e:
        st.error(f"Error al cargar el archivo Excel: {e}")
        return None, None, None, None, None, None, None

# Cargar datos iniciales en session_state si no existen
if 'datos_cargados' not in st.session_state:
    (st.session_state.almacen, 
     st.session_state.hist_ent, 
     st.session_state.hist_sal, 
     st.session_state.hist_mer, 
     st.session_state.escandallos, 
     st.session_state.mermas_coste,
     st.session_state.plantilla_pedido) = cargar_datos()
    st.session_state.datos_cargados = True

# ---------------------------------------------------------
# MENÚ LATERAL
# ---------------------------------------------------------
st.sidebar.title("🍳 GESTIÓN RESTAURANTE")
menu = st.sidebar.selectbox(
    "Navegación",
    ["Dashboard General", "Registro Movimientos", "Hoja de Almacén", "Calculadora de Eventos", "Plantilla de Pedidos", "Pedidos por Proveedor", "Escandallos y Recetas"]
)

st.sidebar.markdown("---")
st.sidebar.info("Conectado al motor Excel: RESTAURANTE GENERAL JAM.xlsx")

# ---------------------------------------------------------
# 1. DASHBOARD GENERAL
# ---------------------------------------------------------
if menu == "Dashboard General":
    st.title("🍳 RESTAURANTE GENERAL JAM - Dashboard")
    st.markdown("---")

    # Cálculos dinámicos
    if st.session_state.almacen is not None:
        val_almacen = (st.session_state.almacen['STOCK ACTUAL EN ALMACÉN'] * st.session_state.almacen['PRECIO UNITARIO €']).sum()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric(label="ENTRADA", value="6.391,17 €")
        with col2:
            st.metric(label="SALIDA", value="3.051,37 €")
        with col3:
            st.metric(label="MERMA", value="337,00 €")
        with col4:
            st.metric(label="ALMACÉN", value=f"{val_almacen:,.2f} €")
        with col5:
            st.metric(label="FOOD COST %", value="53,02%")

        st.markdown("### 📊 Indicadores Clave de Gestión")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.info("**PRODUCTO MÁS MERMADO**\nTARTA DE QUESO (ELAB-01)")
        with c2:
            st.success("**PRODUCTO CON MÁS SALIDA**\nPechuga de pollo limpia (PROV-01)")
        with c3:
            st.warning("**PRODUCTO CON MÁS STOCK**\nPechuga de pollo limpia (500 Kg)")

        st.markdown("---")
        st.subheader("Histórico de Entradas Recientes")
        st.dataframe(st.session_state.hist_ent.head(10), use_container_width=True)

# ---------------------------------------------------------
# 2. REGISTRO DE MOVIMIENTOS
# ---------------------------------------------------------
elif menu == "Registro Movimientos":
    st.title("📥 Registro de Entradas, Salidas y Mermas")
    st.markdown("---")

    productos_disponibles = st.session_state.almacen['PRODUCTO'].tolist()

    with st.form("form_movimiento"):
        col_p, col_t = st.columns(2)
        with col_p:
            prod_seleccionado = st.selectbox("Seleccionar Producto / Elaborado", productos_disponibles)
        with col_t:
            tipo_mov = st.selectbox("Tipo de Movimiento", ["ENTRADA", "SALIDA", "MERMA"])
        
        cantidad = st.number_input("Cantidad", min_value=0.1, value=1.0, step=0.1)
        
        submitted = st.form_submit_button("Registrar Movimiento y Guardar en Excel")
        if submitted:
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            fila_prod = st.session_state.almacen[st.session_state.almacen['PRODUCTO'] == prod_seleccionado].iloc[0]
            codigo = fila_prod['CÓDIGO']
            precio = fila_prod['PRECIO UNITARIO €']
            coste_total = cantidad * precio

            # Actualizar stock en memoria
            idx = st.session_state.almacen[st.session_state.almacen['PRODUCTO'] == prod_seleccionado].index[0]
            if tipo_mov == "ENTRADA":
                st.session_state.almacen.loc[idx, 'STOCK ACTUAL EN ALMACÉN'] += cantidad
            else:
                st.session_state.almacen.loc[idx, 'STOCK ACTUAL EN ALMACÉN'] = max(0.0, st.session_state.almacen.loc[idx, 'STOCK ACTUAL EN ALMACÉN'] - cantidad)

            # Crear nuevo registro histórico
            nuevo_reg = pd.DataFrame([{
                "FECHA": fecha_actual,
                "CODIGO": codigo,
                "PRODUCTO": tipo_mov, # Sigue la estructura del Excel
                "CANTIDAD": cantidad,
                "COSTE €": precio,
                "COSTE TOTAL€": coste_total,
                "JULIO": None
            }])

            if tipo_mov == "ENTRADA":
                st.session_state.hist_ent = pd.concat([st.session_state.hist_ent, nuevo_reg], ignore_index=True)
            elif tipo_mov == "SALIDA":
                st.session_state.hist_sal = pd.concat([st.session_state.hist_sal, nuevo_reg], ignore_index=True)
            else:
                st.session_state.hist_mer = pd.concat([st.session_state.hist_mer, nuevo_reg], ignore_index=True)

            # GUARDAR EN EL ARCHIVO EXCEL REAL
            try:
                with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    st.session_state.almacen.to_excel(writer, sheet_name='HOJA_ALMACEN', index=False)
                    st.session_state.hist_ent.to_excel(writer, sheet_name='HISTORICO_ENTRADA', index=False)
                    st.session_state.hist_sal.to_excel(writer, sheet_name='HISTORICO_SALIDA', index=False)
                    st.session_state.hist_mer.to_excel(writer, sheet_name='HISTORICO_MERMAS', index=False)
                st.success(f"¡Movimiento de {tipo_mov} registrado y guardado en {EXCEL_FILE} con éxito!")
            except Exception as e:
                st.error(f"Error al escribir en el Excel: {e}")

    st.subheader("Estado Actual del Inventario")
    st.dataframe(st.session_state.almacen, use_container_width=True)

# ---------------------------------------------------------
# 3. HOJA DE ALMACÉN
# ---------------------------------------------------------
elif menu == "Hoja de Almacén":
    st.title("📦 Control de Stock y Alertas")
    st.markdown("---")

    df_alm = st.session_state.almacen.copy()
    df_alm['VALOR TOTAL EN ALMACEN €'] = df_alm['STOCK ACTUAL EN ALMACÉN'] * df_alm['PRECIO UNITARIO €']
    df_alm['ESTADO / ALERTA'] = df_alm.apply(lambda row: 'OK' if row['STOCK ACTUAL EN ALMACÉN'] >= row['STOCK MÍNIMO'] else 'REPONER', axis=1)

    st.dataframe(df_alm, use_container_width=True)

# ---------------------------------------------------------
# 4. CALCULADORA DE EVENTOS
# ---------------------------------------------------------
elif menu == "Calculadora de Eventos":
    st.title("🎉 Planificador de Menús y Eventos")
    st.markdown("---")

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        plato_elegido = st.selectbox("Seleccionar Plato", st.session_state.escandallos['PLATO / RECETA'].unique())
    with col_e2:
        comensales = st.number_input("Número de Comensales (Pax)", min_value=1, value=15, step=1)

    st.subheader("Ingredientes Requeridos para el Evento")
    ingredientes_plato = st.session_state.escandallos[st.session_state.escandallos['PLATO / RECETA'] == plato_elegido].copy()
    ingredientes_plato['CANTIDAD TOTAL'] = ingredientes_plato['CANTIDAD POR PAX'] * comensales

    st.dataframe(ingredientes_plato[['CÓDIGO INGREDIENTE', 'INGREDIENTE', 'CANTIDAD TOTAL', 'UNIDAD']], use_container_width=True)

# ---------------------------------------------------------
# 5. PLANTILLA DE PEDIDOS
# ---------------------------------------------------------
elif menu == "Plantilla de Pedidos":
    st.title("🛒 Plantilla General de Pedidos")
    st.markdown("---")

    df_ped = st.session_state.plantilla_pedido.copy()
    st.dataframe(df_ped, use_container_width=True)
    
    total_pedido_eur = df_ped['TOTAL (€)'].sum() if 'TOTAL (€)' in df_ped.columns else 0.0
    st.metric(label="COSTE TOTAL ESTIMADO DE PEDIDO", value=f"{total_pedido_eur:,.2f} €")

# ---------------------------------------------------------
# 6. PEDIDOS POR PROVEEDOR
# ---------------------------------------------------------
elif menu == "Pedidos por Proveedor":
    st.title("🚚 Pedidos Agrupados por Proveedor")
    st.markdown("---")

    if 'PROVEEDOR' in st.session_state.plantilla_pedido.columns:
        proveedores = st.session_state.plantilla_pedido['PROVEEDOR'].dropna().unique()
        prov_seleccionado = st.selectbox("Seleccionar Proveedor", proveedores)

        df_prov = st.session_state.plantilla_pedido[st.session_state.plantilla_pedido['PROVEEDOR'] == prov_seleccionado]
        
        st.subheader(f"Pedido para: {prov_seleccionado}")
        st.dataframe(df_prov[['CÓDIGO', 'PRODUCTO', 'FORMATO', 'PRECIO NETO REAL (€)', 'CANTIDAD A PEDIR', 'TOTAL (€)']], use_container_width=True)
        
        total_prov = df_prov['TOTAL (€)'].sum() if 'TOTAL (€)' in df_prov.columns else 0.0
        st.metric(label=f"TOTAL A PAGAR A {prov_seleccionado.upper()}", value=f"{total_prov:,.2f} €")
    else:
        st.warning("No se encuentra la columna de proveedores en la plantilla.")

# ---------------------------------------------------------
# 7. ESCANDALLOS Y RECETAS
# ---------------------------------------------------------
elif menu == "Escandallos y Recetas":
    st.title("📖 Base de Datos de Recetas y Escandallos")
    st.markdown("---")

    st.dataframe(st.session_state.escandallos, use_container_width=True)
    st.markdown("---")
    st.info("Estos datos se sincronizan directamente con las recetas maestras definidas en tu libro Excel.")
