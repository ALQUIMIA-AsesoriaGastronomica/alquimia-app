import streamlit as str_module
import pandas as pd
import sqlite3
from datetime import datetime, date, timedelta
import urllib.parse
from PIL import Image
import os

DB_NAME = "general_jam.db"

def inicializar_tabla_configuracion():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracion_sistema (
            CLAVE TEXT PRIMARY KEY,
            VALOR TEXT
        )
    """)
    conn.commit()
    conn.close()

inicializar_tabla_configuracion()

def obtener_logo_actual():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT VALOR FROM configuracion_sistema WHERE CLAVE = 'LOGO_ACTUAL'")
        res = cursor.fetchone()
        conn.close()
        if res and res[0] and os.path.exists(res[0]):
            return res[0]
    except:
        pass
    
    for nombre_archivo in ["logo_transparente.png", "logo_3.png", "logo_2.png", "logo.png"]:
        if os.path.exists(nombre_archivo):
            return nombre_archivo
            
    ruta_absoluta = "/Users/macdejose/Desktop/RESTAURANTE GENERAL JAM/logo_transparente.png"
    if os.path.exists(ruta_absoluta):
        return ruta_absoluta
    ruta_alternativa = "/Users/macdejose/Desktop/RESTAURANTE GENERAL JAM/logo.png"
    if os.path.exists(ruta_alternativa):
        return ruta_alternativa
        
    return None

logo_path_actual = obtener_logo_actual()
logo_img = None
if logo_path_actual:
    try:
        logo_img = Image.open(logo_path_actual).convert("RGBA")
    except Exception:
        logo_img = None

str_module.set_page_config(
    page_title="Alquimia - GENERAL JAM (Software De Gestión Integral De Hostelería y Restauración Organizada)",
    page_icon=logo_img if logo_img else "🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

str_module.markdown("""
    <style>
        .stApp { background-color: #0b0f19; color: #f3f4f6; }
        [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1f2937; }
        
        [data-testid="stSidebar"] [data-testid="stImage"] {
            display: flex;
            justify-content: center;
            align-content: center;
            margin-bottom: 10px;
        }
        [data-testid="stSidebar"] img {
            border-radius: 50% !important;
            object-fit: cover !important;
            width: 130px !important;
            height: 130px !important;
            background-color: #1f2937 !important;
            padding: 4px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
            border: 2px solid #38bdf8 !important;
        }

        h1, h2, h3 { color: #ffffff !important; font-family: 'Inter', sans-serif; }
        .stButton button {
            background-color: #3b82f6;
            color: white;
            border-radius: 8px;
            font-weight: 600;
            border: none;
            padding: 0.5rem 1rem;
        }
        .stButton button:hover {
            background-color: #2563eb;
        }
    </style>
""", unsafe_allow_html=True)

def inicializar_base_datos():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hoja_almacen (
            PROVEEDOR TEXT,
            CÓDIGO TEXT PRIMARY KEY,
            PRODUCTO TEXT,
            UNIDAD TEXT,
            [PRECIO UNITARIO €] REAL,
            [STOCK ACTUAL EN ALMACÉN] REAL,
            [STOCK MÍNIMO] REAL,
            [GASTO MENSUAL €] REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS escandallos_precios (
            CÓDIGO TEXT PRIMARY KEY,
            PRODUCTO TEXT,
            [PRECIO BRUTO] REAL,
            [MERMA %] REAL,
            [PRECIO NETO] REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimientos_almacen (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            FECHA TEXT,
            TIPO TEXT,
            CÓDIGO TEXT,
            PRODUCTO TEXT,
            CANTIDAD REAL,
            UNIDAD TEXT,
            MOTIVO TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mermas_almacen (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            FECHA TEXT,
            TIPO_MERMA TEXT,
            CÓDIGO TEXT,
            PRODUCTO TEXT,
            CANTIDAD REAL,
            UNIDAD TEXT,
            OBSERVACIONES TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recetas_cabecera (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CODIGO_RECETA TEXT,
            NOMBRE_RECETA TEXT UNIQUE
        )
    """)
    try:
        cursor.execute("ALTER TABLE recetas_cabecera ADD COLUMN CODIGO_RECETA TEXT")
    except:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recetas_ingredientes (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NOMBRE_RECETA TEXT,
            CODIGO_PRODUCTO TEXT,
            PRODUCTO TEXT,
            CANTIDAD REAL,
            UNIDAD TEXT,
            FOREIGN KEY(NOMBRE_RECETA) REFERENCES recetas_cabecera(NOMBRE_RECETA) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proveedores_contactos (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NOMBRE_PROVEEDOR TEXT UNIQUE,
            CONTACTO TEXT,
            TELEFONO TEXT,
            CORREO TEXT,
            FORMA_ENVIO TEXT,
            DIAS_PEDIDO TEXT
        )
    """)
    try:
        cursor.execute("ALTER TABLE proveedores_contactos ADD COLUMN DIAS_PEDIDO TEXT")
    except:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_pedidos (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NUMERO_PEDIDO TEXT UNIQUE,
            FECHA TEXT,
            PROVEEDOR TEXT,
            DETALLE_PEDIDO TEXT,
            COSTE_TOTAL REAL,
            ESTADO TEXT
        )
    """)
    try:
        cursor.execute("ALTER TABLE historial_pedidos ADD COLUMN NUMERO_PEDIDO TEXT")
        cursor.execute("ALTER TABLE historial_pedidos ADD COLUMN ESTADO TEXT")
    except:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_ingenieria (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CODIGO_RECETA TEXT UNIQUE,
            NOMBRE_RECETA TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos_cabecera (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NOMBRE_EVENTO TEXT UNIQUE,
            FECHA_EVENTO TEXT,
            COMENSALES INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos_items (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NOMBRE_EVENTO TEXT,
            NOMBRE_RECETA TEXT,
            CANTIDAD_UNIDADES REAL,
            FOREIGN KEY(NOMBRE_EVENTO) REFERENCES eventos_cabecera(NOMBRE_EVENTO) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facturacion_ingresos (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            FECHA TEXT,
            CONCEPTO TEXT,
            CATEGORIA TEXT,
            BASE_IMPONIBLE REAL,
            TIPO_IVA REAL,
            TOTAL REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gestoria_documentos (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            FECHA TEXT,
            TIPO TEXT,
            DESCRIPCION TEXT,
            ESTADO TEXT,
            IMPORTE REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS precios_pendientes_validacion (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            FECHA TEXT,
            PROVEEDOR TEXT,
            CÓDIGO TEXT,
            PRODUCTO TEXT,
            PRECIO_ACTUAL REAL,
            PRECIO_NUEVO REAL,
            ESTADO TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS control_albaranes_facturas (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            FECHA TEXT,
            PROVEEDOR TEXT,
            NUMERO_PEDIDO TEXT,
            NUMERO_ALBARAN TEXT UNIQUE,
            IMPORTE_ALBARAN REAL,
            TIENE_FACTURA TEXT,
            NUMERO_FACTURA TEXT
        )
    """)

    conn.commit()
    conn.close()

inicializar_base_datos()

def ejecutar_sql(query, params=(), fetch=True):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query, params)
    if fetch:
        data = cursor.fetchall()
        cols = [description[0] for description in cursor.description]
        conn.close()
        return pd.DataFrame(data, columns=cols)
    else:
        conn.commit()
        conn.close()

def buscar_columna(df, posibles):
    cols_limpias = {c.strip().lower().replace(' ', '_'): c for c in df.columns}
    for p in posibles:
        p_limpio = p.strip().lower().replace(' ', '_')
        if p_limpio in cols_limpias:
            return cols_limpias[p_limpio]
    return None

def calcular_coste_receta(nombre_receta):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ri.CANTIDAD, COALESCE(ha.[PRECIO UNITARIO €], 0.0) 
        FROM recetas_ingredientes ri
        LEFT JOIN hoja_almacen ha ON ri.CODIGO_PRODUCTO = ha.CÓDIGO
        WHERE ri.NOMBRE_RECETA = ?
    """, (nombre_receta,))
    filas = cursor.fetchall()
    conn.close()
    return sum(cant * precio for cant, precio in filas)

if "autenticado" not in str_module.session_state:
    str_module.session_state["autenticado"] = False
    str_module.session_state["rol"] = None

# Forzamos el acceso automático en Modo Administrador para cumplir estrictamente con tu petición
str_module.session_state["autenticado"] = True
str_module.session_state["rol"] = "admin"

if logo_img:
    str_module.sidebar.image(logo_img, use_container_width=True)

str_module.sidebar.markdown("""
    <div style="text-align: center;">
        <p style='color: #38bdf8; font-size: 0.95rem; font-weight: bold; margin-top: 5px; margin-bottom: 0px;'>📍 Restaurante: General Jam</p>
        <p style='color: #9ca3af; font-size: 0.8rem; margin-top: 0px;'>by J.A.Torres chef</p>
    </div>
""", unsafe_allow_html=True)

str_module.sidebar.markdown("<p style='color: #38bdf8; font-size: 0.85rem; text-align: center;'>🔓 Modo: Administrador (Chef)</p>", unsafe_allow_html=True)

with str_module.sidebar.expander("⚙️ Configuración Rápida de Logos"):
    archivo_subido_logo = str_module.file_uploader("Subir nuevo logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
    if archivo_subido_logo is not None:
        try:
            nombre_guardado = f"logo_custom_{archivo_subido_logo.name}"
            with open(nombre_guardado, "wb") as f:
                f.write(archivo_subido_logo.getbuffer())
            
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO configuracion_sistema (CLAVE, VALOR)
                VALUES ('LOGO_ACTUAL', ?)
            """, (nombre_guardado,))
            conn.commit()
            conn.close()
            str_module.success("¡Logo actualizado con éxito! Recargando...")
            str_module.rerun()
        except Exception as e:
            str_module.error(f"Error al guardar logo: {e}")
    
    logos_locales_disponibles = [f for f in ["logo_transparente.png", "logo_3.png", "logo_2.png", "logo.png"] if os.path.exists(f)]
    if logos_locales_disponibles:
        logo_predeterminado_sel = str_module.selectbox("O seleccionar logo existente", logos_locales_disponibles)
        if str_module.button("Aplicar Logo Existente"):
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO configuracion_sistema (CLAVE, VALOR)
                    VALUES ('LOGO_ACTUAL', ?)
                """, (logo_predeterminado_sel,))
                conn.commit()
                conn.close()
                str_module.success("¡Logo predeterminado aplicado! Recargando...")
                str_module.rerun()
            except Exception as e:
                str_module.error(f"Error: {e}")

str_module.sidebar.markdown("---")
if str_module.sidebar.button("🔒 Cerrar Sesión"):
    str_module.session_state["autenticado"] = False
    str_module.session_state["rol"] = None
    str_module.rerun()

pestana_principal, pestana_escandallos, pestana_movimientos, pestana_mermas, pestana_recetas, pestana_ingenieria, pestana_eventos, pestana_pedidos, pestana_facturacion = str_module.tabs([
    "📦 Inventario y Almacén", 
    "📊 Escandallos / Precios",
    "🔄 Entradas / Salidas de Género", 
    "🗑️ Control de Mermas",
    "📖 Recetas",
    "📈 Ingeniería de Menú",
    "🎉 Eventos / Menús Cerrados",
    "🛒 Gestión de Pedidos",
    "📑 Facturación y Gestoría"
])

with pestana_principal:
    str_module.title("📦 Hoja de Almacén e Inventario General")
    str_module.markdown("Control centralizado de stock, reposiciones, costes y referencias con desglose automático de productos **ELAB** por ingredientes de recetas.")
    str_module.markdown("---")

    with str_module.expander("🔔 Alertas y Validación de Nuevos Precios de Proveedores"):
        df_pendientes_precios = ejecutar_sql("SELECT * FROM precios_pendientes_validacion WHERE ESTADO = 'PENDIENTE'")
        if not df_pendientes_precios.empty:
            str_module.warning(f"Hay {len(df_pendientes_precios)} modificaciones de precios detectadas pendientes de tu aprobación.")
            
            for _, row_p in df_pendientes_precios.iterrows():
                col_ap1, col_ap2, col_ap3 = str_module.columns([3, 2, 2])
                with col_ap1:
                    str_module.markdown(f"**{row_p['PRODUCTO']}** ({row_p['PROVEEDOR']})")
                    str_module.text(f"Actual: {row_p['PRECIO_ACTUAL']} € ➡️ Nuevo detectado: {row_p['PRECIO_NUEVO']} €")
                with col_ap2:
                    if str_module.button(f"✅ Aprobar", key=f"aprob_{row_p['ID']}"):
                        conn = sqlite3.connect(DB_NAME)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE hoja_almacen SET [PRECIO UNITARIO €] = ? WHERE CÓDIGO = ?", (row_p['PRECIO_NUEVO'], row_p['CÓDIGO']))
                        cursor.execute("UPDATE precios_pendientes_validacion SET ESTADO = 'APROBADO' WHERE ID = ?", (row_p['ID'],))
                        conn.commit()
                        conn.close()
                        str_module.success("¡Precio actualizado!")
                        str_module.rerun()
                with col_ap3:
                    if str_module.button(f"❌ Descartar", key=f"desc_{row_p['ID']}"):
                        conn = sqlite3.connect(DB_NAME)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE precios_pendientes_validacion SET ESTADO = 'DESCARTADO' WHERE ID = ?", (row_p['ID'],))
                        conn.commit()
                        conn.close()
                        str_module.info("Cambio descartado.")
                        str_module.rerun()
        else:
            str_module.info("No hay cambios de precios pendientes de revisión.")

    tab_nuevo, tab_eliminar = str_module.tabs(["➕ Añadir Nueva Referencia", "🗑️ Eliminar Referencias Antiguas"])
    
    with tab_nuevo:
        with str_module.form("form_nueva_ref"):
            c1, c2, c3 = str_module.columns(3)
            with c1:
                prov_input = str_module.text_input("Proveedor", value="")
                codigo_input = str_module.text_input("Código (Ej: PROV-01 o ELAB-01)")
                producto_input = str_module.text_input("Nombre del Producto")
            with c2:
                unidad_input = str_module.selectbox("Unidad de Medida", ["Kg", "Litro", "Unidad", "Gramos", "Cl"])
                precio_input = str_module.text_input("Precio Unitario (€)", value="0.0")
                stock_act_input = str_module.text_input("Stock Actual", value="0.0")
            with c3:
                stock_min_input = str_module.text_input("Stock Mínimo", value="0.0")
                gasto_mensual_input = str_module.text_input("Gasto Mensual Estimado (€)", value="0.0")

            btn_guardar_ref = str_module.form_submit_button("💾 Guardar Referencia en Base de Datos")

            if btn_guardar_ref:
                if not codigo_input or not producto_input:
                    str_module.error("Por favor, rellena al menos el Código y el Nombre del producto.")
                else:
                    try:
                        def limpiar_float(val):
                            val_str = str(val).strip().replace(',', '.')
                            return float(val_str) if val_str else 0.0

                        p_val = limpiar_float(precio_input)
                        s_act = limpiar_float(stock_act_input)
                        s_min = limpiar_float(stock_min_input)
                        g_mes = limpiar_float(gasto_mensual_input)

                        conn = sqlite3.connect(DB_NAME)
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT OR REPLACE INTO hoja_almacen (PROVEEDOR, CÓDIGO, PRODUCTO, UNIDAD, [PRECIO UNITARIO €], [STOCK ACTUAL EN ALMACÉN], [STOCK MÍNIMO], [GASTO MENSUAL €])
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (prov_input, codigo_input, producto_input, unidad_input, p_val, s_act, s_min, g_mes))
                        conn.commit()
                        conn.close()
                        str_module.success(f"¡Referencia '{producto_input}' guardada con éxito!")
                        str_module.rerun()
                    except Exception as e:
                        str_module.error(f"Error al guardar: {e}")

    with tab_eliminar:
        df_actual = ejecutar_sql("SELECT CÓDIGO, PRODUCTO FROM hoja_almacen")
        if not df_actual.empty:
            opciones_eliminar = [f"{row['CÓDIGO']} - {row['PRODUCTO']}" for _, row in df_actual.iterrows()]
            with str_module.form("form_eliminar_ref"):
                ref_a_borrar = str_module.selectbox("Selecciona la referencia que deseas eliminar", opciones_eliminar)
                btn_borrar = str_module.form_submit_button("🗑️ Eliminar Referencia Seleccionada")
                
                if btn_borrar and ref_a_borrar:
                    codigo_a_quitar = ref_a_borrar.split(" - ")[0]
                    try:
                        conn = sqlite3.connect(DB_NAME)
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM hoja_almacen WHERE CÓDIGO = ?", (codigo_a_quitar,))
                        conn.commit()
                        conn.close()
                        str_module.success(f"¡Referencia '{ref_a_borrar}' eliminada correctamente!")
                        str_module.rerun()
                    except Exception as e:
                        str_module.error(f"Error al eliminar: {e}")
        else:
            str_module.info("No hay referencias registradas para eliminar.")

    str_module.markdown("---")
    df_alm = ejecutar_sql("SELECT * FROM hoja_almacen")

    if not df_alm.empty:
        col_prov = buscar_columna(df_alm, ['proveedor', 'proveedores'])
        col_cod = buscar_columna(df_alm, ['código', 'codigo', 'id'])
        col_prod = buscar_columna(df_alm, ['producto', 'articulo', 'nombre'])
        col_uni = buscar_columna(df_alm, ['unidad', 'ud'])
        col_pre = buscar_columna(df_alm, ['precio_unitario_eur', 'precio', 'precio_unitario'])
        col_stk = buscar_columna(df_alm, ['stock_actual_en_almacén', 'stock', 'stock_actual', 'existencias'])
        col_min = buscar_columna(df_alm, ['stock_mínimo', 'minimo'])
        col_gasto = buscar_columna(df_alm, ['gasto_mensual', 'gasto_mensual_eur', 'gasto'])

        cols_a_borrar = [c for c in df_alm.columns if 'TOTAL' in c.upper() and 'PEDIR' not in c.upper() and 'TOTAL A PEDIR' not in c.upper()]
        df_alm = df_alm.drop(columns=cols_a_borrar, errors='ignore')

        if not col_prov:
            df_alm['PROVEEDOR'] = ""
            col_prov = 'PROVEEDOR'

        deficit_elab_dict = {} 
        
        for _, row_item in df_alm.iterrows():
            codigo_ref = str(row_item[col_cod]).upper() if col_cod and pd.notna(row_item[col_cod]) else ""
            proveedor_ref = str(row_item[col_prov]).upper() if col_prov and pd.notna(row_item[col_prov]) else ""
            stock_val = float(str(row_item[col_stk]).replace(',', '.')) if col_stk and pd.notna(row_item[col_stk]) else 0.0
            min_val = float(str(row_item[col_min]).replace(',', '.')) if col_min and pd.notna(row_item[col_min]) else 0.0
            
            if "ELAB" in codigo_ref or "PRODUCCIÓN INTERNA" in proveedor_ref:
                if stock_val < min_val:
                    deficit_elab = min_val - stock_val
                    nombre_receta_elab = str(row_item[col_prod])
                    
                    df_receta_ings = ejecutar_sql("""
                        SELECT CODIGO_PRODUCTO, CANTIDAD 
                        FROM recetas_ingredientes 
                        WHERE NOMBRE_RECETA = ? OR NOMBRE_RECETA IN (
                            SELECT NOMBRE_RECETA FROM recetas_cabecera WHERE CODIGO_RECETA = ?
                        )
                    """, (nombre_receta_elab, codigo_ref))
                    
                    for _, ing_row in df_receta_ings.iterrows():
                        ing_cod = ing_row['CODIGO_PRODUCTO']
                        ing_cant_unitaria = float(ing_row['CANTIDAD'])
                        deficit_elab_dict[ing_cod] = deficit_elab_dict.get(ing_cod, 0.0) + (ing_cant_unitaria * deficit_elab)

        df_eventos_activos = ejecutar_sql("SELECT NOMBRE_EVENTO, FECHA_EVENTO FROM eventos_cabecera")
        necesidades_eventos_dict = {}
        if not df_eventos_activos.empty:
            dias_nieves_str = "LUNES, VIERNES"
            df_prov_nieves = ejecutar_sql("SELECT DIAS_PEDIDO FROM proveedores_contactos WHERE NOMBRE_PROVEEDOR = 'NIEVES'")
            if not df_prov_nieves.empty and pd.notna(df_prov_nieves.iloc[0]['DIAS_PEDIDO']):
                dias_nieves_str = str(df_prov_nieves.iloc[0]['DIAS_PEDIDO'])
            
            def obtener_fecha_pedido_mas_cercana(fecha_evento_str, dias_str):
                try:
                    f_evento = datetime.strptime(fecha_evento_str, "%Y-%m-%d").date()
                except:
                    return None
                
                map_dias = {'LUNES': 0, 'MARTES': 1, 'MIERCOLES': 2, 'MIÉRCOLES': 2, 'JUEVES': 3, 'VIERNES': 4, 'SABADO': 5, 'SÁBADO': 5, 'DOMINGO': 6}
                dias_habiles = []
                for d in dias_str.split(','):
                    d_clean = d.strip().upper()
                    if d_clean in map_dias:
                        dias_habiles.append(map_dias[d_clean])
                
                if not dias_habiles:
                    dias_habiles = [0, 4]
                
                current_date = f_evento
                for _ in range(14):
                    if current_date.weekday() in dias_habiles:
                        return current_date
                    current_date -= timedelta(days=1)
                return f_evento

            hoy = date.today()
            df_all_items = ejecutar_sql("SELECT NOMBRE_EVENTO, NOMBRE_RECETA, CANTIDAD_UNIDADES FROM eventos_items")
            for _, item in df_all_items.iterrows():
                n_ev = item['NOMBRE_EVENTO']
                n_rec = item['NOMBRE_RECETA']
                cant_un = float(item['CANTIDAD_UNIDADES'])
                
                m_ev = df_eventos_activos[df_eventos_activos['NOMBRE_EVENTO'] == n_ev]
                if not m_ev.empty:
                    f_ev_str = m_ev.iloc[0]['FECHA_EVENTO']
                    try:
                        f_ev_date = datetime.strptime(f_ev_str, "%Y-%m-%d").date()
                    except:
                        continue
                    
                    if f_ev_date < hoy:
                        continue
                    
                    f_pedido_cercana = obtener_fecha_pedido_mas_cercana(f_ev_str, dias_nieves_str)
                    
                    if f_pedido_cercana and hoy >= f_pedido_cercana:
                        df_ings = ejecutar_sql("SELECT CODIGO_PRODUCTO, CANTIDAD FROM recetas_ingredientes WHERE NOMBRE_RECETA = ?", (n_rec,))
                        for _, ing in df_ings.iterrows():
                            c_prod = ing['CODIGO_PRODUCTO']
                            c_cant = float(ing['CANTIDAD']) * cant_un
                            necesidades_eventos_dict[c_prod] = necesidades_eventos_dict.get(c_prod, 0.0) + c_cant

        def calcular_filas(row):
            try:
                stock = float(str(row[col_stk]).replace(',', '.')) if col_stk and pd.notna(row[col_stk]) else 0.0
                minimo = float(str(row[col_min]).replace(',', '.')) if col_min and pd.notna(row[col_min]) else 0.0
                precio = float(str(row[col_pre]).replace(',', '.')) if col_pre and pd.notna(row[col_pre]) else 0.0
                codigo_val = str(row[col_cod]).upper() if col_cod and pd.notna(row[col_cod]) else ""
                proveedor_val = str(row[col_prov]).upper() if col_prov and pd.notna(row[col_prov]) else ""
            except Exception:
                stock, minimo, precio = 0.0, 0.0, 0.0
                codigo_val, proveedor_val = "", ""

            nec_evento = necesidades_eventos_dict.get(codigo_val, 0.0)
            deficit_derivado_elab = deficit_elab_dict.get(codigo_val, 0.0)

            if "ELAB" in codigo_val or "PRODUCCIÓN INTERNA" in proveedor_val:
                total_a_pedir = max(0.0, minimo - stock) if stock < minimo else 0.0
            else:
                total_a_pedir = max(0.0, (minimo + nec_evento + deficit_derivado_elab) - stock) if stock < (minimo + nec_evento + deficit_derivado_elab) else 0.0

            precio_total = stock * precio

            if stock >= minimo and nec_evento == 0 and deficit_derivado_elab == 0:
                estado = "🟢 OK"
            elif stock < minimo or nec_evento > 0 or deficit_derivado_elab > 0:
                if "ELAB" in codigo_val or "PRODUCCIÓN INTERNA" in proveedor_val:
                    estado = "🟡 ELABORAR"
                else:
                    estado = "🔴 REPONER"
            else:
                estado = "🟢 OK"

            return pd.Series([nec_evento, total_a_pedir, precio_total, estado])

        df_alm[['EVENTOS / MENÚS CERRADOS', 'TOTAL A PEDIR', 'PRECIO TOTAL €', 'ESTADO / ALERTA']] = df_alm.apply(calcular_filas, axis=1)

        columnas_ordenadas = []
        if col_prov in df_alm.columns: columnas_ordenadas.append(col_prov)
        if col_cod in df_alm.columns: columnas_ordenadas.append(col_cod)
        if col_prod in df_alm.columns: columnas_ordenadas.append(col_prod)
        if col_uni in df_alm.columns: columnas_ordenadas.append(col_uni)
        if col_pre in df_alm.columns: columnas_ordenadas.append(col_pre)
        if col_stk in df_alm.columns: columnas_ordenadas.append(col_stk)
        if col_min in df_alm.columns: columnas_ordenadas.append(col_min)
        if 'EVENTOS / MENÚS CERRADOS' in df_alm.columns: columnas_ordenadas.append('EVENTOS / MENÚS CERRADOS')
        if 'TOTAL A PEDIR' in df_alm.columns: columnas_ordenadas.append('TOTAL A PEDIR')
        if 'PRECIO TOTAL €' in df_alm.columns: columnas_ordenadas.append('PRECIO TOTAL €')
        if col_gasto in df_alm.columns: columnas_ordenadas.append(col_gasto)
        if 'ESTADO / ALERTA' in df_alm.columns: columnas_ordenadas.append('ESTADO / ALERTA')

        for col in df_alm.columns:
            if col not in columnas_ordenadas:
                columnas_ordenadas.append(col)

        df_final = df_alm[columnas_ordenadas]

        str_module.markdown("### ✏️ Edición de Stock Mínimo")
        str_module.info("💡 Haz doble clic sobre cualquier celda de la columna **STOCK MÍNIMO** para modificar su valor directamente. Los productos **ELAB** desglosarán automáticamente sus necesidades en los ingredientes base.")
        disabled_cols = [c for c in df_final.columns if c != col_min]

        edited_df = str_module.data_editor(
            df_final,
            use_container_width=True,
            hide_index=True,
            disabled=disabled_cols,
            key="editor_almacen_stock_min"
        )

        if str_module.button("💾 Guardar Cambios en Stock Mínimo"):
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                for _, row in edited_df.iterrows():
                    codigo_val = row[col_cod]
                    nuevo_min_val = float(str(row[col_min]).replace(',', '.') if pd.notna(row[col_min]) else 0.0)
                    cursor.execute(f"UPDATE hoja_almacen SET [{col_min}] = ? WHERE CÓDIGO = ?", (nuevo_min_val, codigo_val))
                conn.commit()
                conn.close()
                str_module.success("¡Stock mínimo actualizado con éxito y pedidos automatizados por ingredientes!")
                str_module.rerun()
            except Exception as e:
                str_module.error(f"Error al guardar los cambios: {e}")
    else:
        str_module.info("La base de datos está vacía actualmente.")

with pestana_escandallos:
    str_module.title("📊 Escandallos y Precios")
    str_module.markdown("Consulta el registro de escandallos, precios netos y mermas calculadas.")
    str_module.markdown("---")

    df_esc_guardados = ejecutar_sql("SELECT * FROM escandallos_precios")
    if not df_esc_guardados.empty:
        str_module.dataframe(df_esc_guardados, use_container_width=True, hide_index=True)
        
    str_module.markdown("---")
    str_module.markdown("### 📊 Registrar / Actualizar Escandallo")
    df_inv_escandallo = ejecutar_sql("SELECT CÓDIGO, PRODUCTO, [PRECIO UNITARIO €] FROM hoja_almacen")
    if not df_inv_escandallo.empty:
        opciones_inv_esc = [f"{row['CÓDIGO']} - {row['PRODUCTO']}" for _, row in df_inv_escandallo.iterrows()]

        with str_module.form("form_escandallo_precios"):
            ce1, ce2, ce3 = str_module.columns(3)
            with ce1:
                producto_esc_sel = str_module.selectbox("Seleccionar Producto", opciones_inv_esc)
                precio_bruto_input = str_module.text_input("Precio Bruto (€)", value="0.0")
            with ce2:
                merma_input = str_module.text_input("Merma del Producto (%)", value="0.0")
            with ce3:
                str_module.markdown("<br>", unsafe_allow_html=True)
                btn_guardar_esc = str_module.form_submit_button("⚡ Calcular, Registrar y Actualizar Almacén")

            if btn_guardar_esc:
                try:
                    p_bruto = float(str(precio_bruto_input).strip().replace(',', '.') or 0.0)
                    p_merma = float(str(merma_input).strip().replace(',', '.') or 0.0)

                    if p_merma >= 100:
                        str_module.error("La merma no puede ser igual o superior al 100%.")
                    else:
                        denominador = (1.0 - (p_merma / 100.0))
                        precio_neto = p_bruto / denominador if denominador > 0 else p_bruto

                        codigo_prod = producto_esc_sel.split(" - ")[0]
                        nombre_prod = producto_esc_sel.split(" - ")[1]

                        row_actual_prod = df_inv_escandallo[df_inv_escandallo['CÓDIGO'] == codigo_prod]
                        precio_actual_db = float(row_actual_prod.iloc[0]['[PRECIO UNITARIO €]']) if not row_actual_prod.empty and '[PRECIO UNITARIO €]' in row_actual_prod.columns else 0.0

                        conn = sqlite3.connect(DB_NAME)
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT OR REPLACE INTO escandallos_precios (CÓDIGO, PRODUCTO, [PRECIO BRUTO], [MERMA %], [PRECIO NETO])
                            VALUES (?, ?, ?, ?, ?)
                        """, (codigo_prod, nombre_prod, p_bruto, p_merma, precio_neto))

                        if precio_actual_db > 0 and abs(precio_neto - precio_actual_db) > 0.001:
                            cursor.execute("""
                                INSERT INTO precios_pendientes_validacion (FECHA, PROVEEDOR, CÓDIGO, PRODUCTO, PRECIO_ACTUAL, PRECIO_NUEVO, ESTADO)
                                SELECT ?, PROVEEDOR, ?, ?, ?, ?, 'PENDIENTE'
                                FROM hoja_almacen WHERE CÓDIGO = ?
                            """, (date.today().strftime("%Y-%m-%d"), codigo_prod, nombre_prod, precio_actual_db, precio_neto, codigo_prod))
                            str_module.warning("⚠️ Se ha detectado una diferencia con el precio actual. El cambio se ha enviado a la bandeja de validación del administrador.")
                        else:
                            cursor.execute("""
                                UPDATE hoja_almacen SET [PRECIO UNITARIO €] = ? WHERE CÓDIGO = ?
                            """, (precio_neto, codigo_prod))
                            str_module.success(f"¡Precio Neto calculado ({precio_neto:.2f} €), registrado y actualizado en el Almacén para '{nombre_prod}'!")

                        conn.commit()
                        conn.close()
                        str_module.rerun()
                except Exception as e:
                    str_module.error(f"Error al calcular el precio neto: {e}")
    else:
        str_module.info("No hay referencias en el inventario.")

with pestana_movimientos:
    str_module.title("🔄 Entradas / Salidas de Género")
    str_module.markdown("Gestión y registro de entradas y salidas de almacén.")
    str_module.markdown("---")
    
    with str_module.form("form_nuevo_movimiento"):
        cm1, cm2, cm3 = str_module.columns(3)
        with cm1:
            fecha_mov = str_module.date_input("Fecha", value=date.today())
            tipo_mov = str_module.selectbox("Tipo de Movimiento", ["ENTRADA", "SALIDA"])
        with cm2:
            df_inv_mov = ejecutar_sql("SELECT CÓDIGO, PRODUCTO, UNIDAD FROM hoja_almacen")
            if not df_inv_mov.empty:
                opciones_mov = [f"{row['CÓDIGO']} - {row['PRODUCTO']}" for _, row in df_inv_mov.iterrows()]
                prod_mov_sel = str_module.selectbox("Producto", opciones_mov)
            else:
                prod_mov_sel = None
            cantidad_mov = str_module.text_input("Cantidad", value="1.0")
        with cm3:
            motivo_mov = str_module.text_input("Motivo / Referencia (Ej: Factura 123, Venta sala)")
            str_module.markdown("<br>", unsafe_allow_html=True)
            btn_guardar_mov = str_module.form_submit_button("💾 Registrar Movimiento y Actualizar Stock")

        if btn_guardar_mov and prod_mov_sel:
            try:
                cant_val = float(str(cantidad_mov).strip().replace(',', '.') or 0.0)
                cod_m = prod_mov_sel.split(" - ")[0]
                nom_m = prod_mov_sel.split(" - ")[1]
                
                match_uni = df_inv_mov[df_inv_mov['CÓDIGO'] == cod_m]
                uni_m = match_uni.iloc[0]['UNIDAD'] if not match_uni.empty else "Unidad"
                f_m_str = fecha_mov.strftime("%Y-%m-%d")

                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO movimientos_almacen (FECHA, TIPO, CÓDIGO, PRODUCTO, CANTIDAD, UNIDAD, MOTIVO)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (f_m_str, tipo_mov, cod_m, nom_m, cant_val, uni_m, motivo_mov))

                if tipo_mov == "ENTRADA":
                    cursor.execute("""
                        UPDATE hoja_almacen SET [STOCK ACTUAL EN ALMACÉN] = [STOCK ACTUAL EN ALMACÉN] + ? WHERE CÓDIGO = ?
                    """, (cant_val, cod_m))
                else:
                    cursor.execute("""
                        UPDATE hoja_almacen SET [STOCK ACTUAL EN ALMACÉN] = MAX(0.0, [STOCK ACTUAL EN ALMACÉN] - ?) WHERE CÓDIGO = ?
                    """, (cant_val, cod_m))

                conn.commit()
                conn.close()
                str_module.success(f"¡Movimiento de {tipo_mov} registrado con éxito y stock actualizado!")
                str_module.rerun()
            except Exception as e:
                str_module.error(f"Error al registrar movimiento: {e}")

    str_module.markdown("---")
    df_movs_visualizar = ejecutar_sql("SELECT * FROM movimientos_almacen ORDER BY ID DESC LIMIT 50")
    if not df_movs_visualizar.empty:
        str_module.dataframe(df_movs_visualizar, use_container_width=True, hide_index=True)
    else:
        str_module.info("No hay registros de entradas/salidas todavía.")

with pestana_mermas:
    str_module.title("🗑️ Control de Mermas")
    str_module.markdown("Registro y control de mermas de almacén con descuento automático de stock.")
    str_module.markdown("---")
    
    with str_module.form("form_nueva_merma"):
        cme1, cme2, cme3 = str_module.columns(3)
        with cme1:
            fecha_merma = str_module.date_input("Fecha Merma", value=date.today())
            tipo_merma = str_module.selectbox("Tipo de Merma", ["Caducidad / Deterioro", "Rotura / Accidente", "Exceso de Limpieza / Preparación", "Otro"])
        with cme2:
            df_inv_merma = ejecutar_sql("SELECT CÓDIGO, PRODUCTO, UNIDAD FROM hoja_almacen")
            if not df_inv_merma.empty:
                opciones_merma = [f"{row['CÓDIGO']} - {row['PRODUCTO']}" for _, row in df_inv_merma.iterrows()]
                prod_merma_sel = str_module.selectbox("Producto afectado", opciones_merma)
            else:
                prod_merma_sel = None
            cant_merma = str_module.text_input("Cantidad Merma", value="1.0")
        with cme3:
            obs_merma = str_module.text_input("Observaciones / Motivo")
            str_module.markdown("<br>", unsafe_allow_html=True)
            btn_guardar_merma = str_module.form_submit_button("🗑️ Registrar Merma y Descontar Stock")

        if btn_guardar_merma and prod_merma_sel:
            try:
                c_val = float(str(cant_merma).strip().replace(',', '.') or 0.0)
                cod_me = prod_merma_sel.split(" - ")[0]
                nom_me = prod_merma_sel.split(" - ")[1]
                
                match_uni_me = df_inv_merma[df_inv_merma['CÓDIGO'] == cod_me]
                uni_me = match_uni_me.iloc[0]['UNIDAD'] if not match_uni_me.empty else "Unidad"
                f_me_str = fecha_merma.strftime("%Y-%m-%d")

                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO mermas_almacen (FECHA, TIPO_MERMA, CÓDIGO, PRODUCTO, CANTIDAD, UNIDAD, OBSERVACIONES)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (f_me_str, tipo_merma, cod_me, nom_me, c_val, uni_me, obs_merma))

                cursor.execute("""
                    UPDATE hoja_almacen SET [STOCK ACTUAL EN ALMACÉN] = MAX(0.0, [STOCK ACTUAL EN ALMACÉN] - ?) WHERE CÓDIGO = ?
                """, (c_val, cod_me))

                conn.commit()
                conn.close()
                str_module.success(f"¡Merma registrada y stock descontado correctamente para '{nom_me}'!")
                str_module.rerun()
            except Exception as e:
                str_module.error(f"Error al registrar merma: {e}")

    str_module.markdown("---")
    df_mermas_visualizar = ejecutar_sql("SELECT * FROM mermas_almacen ORDER BY ID DESC LIMIT 50")
    if not df_mermas_visualizar.empty:
        str_module.dataframe(df_mermas_visualizar, use_container_width=True, hide_index=True)
    else:
        str_module.info("No hay registros de mermas todavía.")

with pestana_recetas:
    str_module.title("📖 Recetario y Creación de Elaboraciones")
    str_module.markdown("Crea recetas, vincula ingredientes desde el almacén y calcula el coste total de producción.")
    str_module.markdown("---")

    sub_crear_receta, sub_ver_receta = str_module.tabs(["➕ Crear / Editar Receta", "📖 Consultar Recetas y Costes"])

    with sub_crear_receta:
        with str_module.form("form_crear_receta_cab"):
            rc1, rc2 = str_module.columns(2)
            with rc1:
                cod_receta_input = str_module.text_input("Código de Receta o Elaboración (Ej: ELAB-01)")
            with rc2:
                nombre_receta_input = str_module.text_input("Nombre de la Receta / Elaboración")
            
            btn_guardar_cabecera = str_module.form_submit_button("💾 Guardar / Registrar Cabecera de Receta")

            if btn_guardar_cabecera:
                if not nombre_receta_input.strip() or not cod_receta_input.strip():
                    str_module.error("El código y el nombre de la receta son obligatorios.")
                else:
                    try:
                        conn = sqlite3.connect(DB_NAME)
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT OR REPLACE INTO recetas_cabecera (CODIGO_RECETA, NOMBRE_RECETA)
                            VALUES (?, ?)
                        """, (cod_receta_input.strip().upper(), nombre_receta_input.strip()))
                        conn.commit()
                        conn.close()
                        str_module.success(f"¡Receta '{nombre_receta_input.strip()}' creada con éxito!")
                        str_module.rerun()
                    except Exception as e:
                        str_module.error(f"Error al guardar receta: {e}")

        str_module.markdown("---")
        str_module.markdown("### 🥣 Añadir Ingrediente a Receta Existente")
        
        df_recetas_existentes = ejecutar_sql("SELECT NOMBRE_RECETA FROM recetas_cabecera")
        df_inv_ing = ejecutar_sql("SELECT CÓDIGO, PRODUCTO, UNIDAD FROM hoja_almacen")

        if not df_recetas_existentes.empty and not df_inv_ing.empty:
            with str_module.form("form_agregar_ingrediente_receta"):
                ri1, ri2, ri3 = str_module.columns(3)
                with ri1:
                    receta_elegida = str_module.selectbox("Seleccionar Receta", df_recetas_existentes['NOMBRE_RECETA'].tolist())
                    opciones_ing = [f"{row['CÓDIGO']} - {row['PRODUCTO']} ({row['UNIDAD']})" for _, row in df_inv_ing.iterrows()]
                    ingrediente_elegido = str_module.selectbox("Seleccionar Ingrediente del Almacén", opciones_ing)
                with ri2:
                    cantidad_ing_receta = str_module.text_input("Cantidad necesaria en la receta", value="1.0")
                with ri3:
                    str_module.markdown("<br>", unsafe_allow_html=True)
                    btn_guardar_ing_receta = str_module.form_submit_button("➕ Añadir Ingrediente a la Receta")

                if btn_guardar_ing_receta:
                    try:
                        cant_n = float(str(cantidad_ing_receta).strip().replace(',', '.') or 0.0)
                        c_prod = ingrediente_elegido.split(" - ")[0]
                        
                        match_prod_rec = df_inv_ing[df_inv_ing['CÓDIGO'] == c_prod]
                        n_prod = match_prod_rec.iloc[0]['PRODUCTO'] if not match_prod_rec.empty else ""
                        u_prod = match_prod_rec.iloc[0]['UNIDAD'] if not match_prod_rec.empty else "Unidad"

                        conn = sqlite3.connect(DB_NAME)
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO recetas_ingredientes (NOMBRE_RECETA, CODIGO_PRODUCTO, PRODUCTO, CANTIDAD, UNIDAD)
                            VALUES (?, ?, ?, ?, ?)
                        """, (receta_elegida, c_prod, n_prod, cant_n, u_prod))
                        conn.commit()
                        conn.close()
                        str_module.success(f"¡Ingrediente '{n_prod}' añadido a '{receta_elegida}' con éxito!")
                        str_module.rerun()
                    except Exception as e:
                        str_module.error(f"Error al añadir ingrediente: {e}")
        else:
            str_module.info("Debes crear al menos una receta y tener referencias en el almacén para añadir ingredientes.")

    with sub_ver_receta:
        df_recetas_cab = ejecutar_sql("SELECT DISTINCT NOMBRE_RECETA, CODIGO_RECETA FROM recetas_cabecera")
        if not df_recetas_cab.empty:
            receta_seleccionada_ver = str_module.selectbox("Selecciona una receta para ver sus ingredientes y escandallo", df_recetas_cab['NOMBRE_RECETA'].tolist())
            
            if receta_seleccionada_ver:
                df_ing_receta = ejecutar_sql("""
                    SELECT ri.CODIGO_PRODUCTO AS CÓDIGO, ri.PRODUCTO, ri.CANTIDAD, ri.UNIDAD, 
                           COALESCE(ha.[PRECIO UNITARIO €], 0.0) AS [PRECIO UNITARIO €],
                           (ri.CANTIDAD * COALESCE(ha.[PRECIO UNITARIO €], 0.0)) AS [COSTE TOTAL €]
                    FROM recetas_ingredientes ri
                    LEFT JOIN hoja_almacen ha ON ri.CODIGO_PRODUCTO = ha.CÓDIGO
                    WHERE ri.NOMBRE_RECETA = ?
                """, (receta_seleccionada_ver,))
                
                str_module.markdown(f"#### 🥣 Ingredientes de: **{receta_seleccionada_ver}**")
                if not df_ing_receta.empty:
                    str_module.dataframe(df_ing_receta, use_container_width=True, hide_index=True)
                    coste_total_receta = df_ing_receta['COSTE TOTAL €'].sum()
                    str_module.markdown(f"### 💰 **Coste Total de Producción:** `{coste_total_receta:.2f} €`")
                else:
                    str_module.info("Esta receta no tiene ingredientes registrados.")
        else:
            str_module.info("Todavía no se ha creado ninguna receta.")

with pestana_ingenieria:
    str_module.title("📈 Ingeniería de Menú (Productos Elaborados)")
    str_module.markdown("Evaluación automática basada en el PVP sin IVA calculado al **27% de Food Cost** sobre la elaboración y las ventas extraídas del registro de salidas.")
    str_module.markdown("---")

    str_module.markdown("### 📅 Filtrar Rango de Fechas para Análisis de Ventas")
    col_f1, col_f2 = str_module.columns(2)
    with col_f1:
        fecha_inicio_menu = str_module.date_input("Fecha de Inicio", value=date.today() - timedelta(days=30), key="menu_fi")
    with col_f2:
        fecha_fin_menu = str_module.date_input("Fecha de Fin", value=date.today(), key="menu_ff")

    str_module.markdown("---")

    df_elaboraciones = ejecutar_sql("SELECT DISTINCT CODIGO_RECETA, NOMBRE_RECETA FROM recetas_cabecera")

    if not df_elaboraciones.empty:
        str_module.markdown("### ⚙️ Registrar Elaboraciones en Ingeniería de Menú")
        with str_module.form("form_config_ingenieria"):
            opciones_elab = [f"{row['CODIGO_RECETA']} - {row['NOMBRE_RECETA']}" for _, row in df_elaboraciones.iterrows()]
            elab_sel = str_module.selectbox("Seleccionar Elaboración a incluir", opciones_elab)
            btn_guardar_ing_menu = str_module.form_submit_button("💾 Añadir/Vincular a Ingeniería de Menú")

            if btn_guardar_ing_menu:
                try:
                    cod_elab = elab_sel.split(" - ")[0]
                    nom_elab = elab_sel.split(" - ")[1]

                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR IGNORE INTO menu_ingenieria (CODIGO_RECETA, NOMBRE_RECETA)
                        VALUES (?, ?)
                    """, (cod_elab, nom_elab))
                    conn.commit()
                    conn.close()

                    str_module.success(f"¡Elaboración '{nom_elab}' vinculada a la ingeniería de menú con éxito!")
                    str_module.rerun()
                except Exception as e:
                    str_module.error(f"Error al guardar datos: {e}")
        str_module.markdown("---")

        df_menu_registrados = ejecutar_sql("SELECT CODIGO_RECETA, NOMBRE_RECETA FROM menu_ingenieria")

        if not df_menu_registrados.empty:
            lista_datos_matriz = []
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            str_fi = fecha_inicio_menu.strftime("%Y-%m-%d")
            str_ff = fecha_fin_menu.strftime("%Y-%m-%d 23:59:59")

            for _, row_m in df_menu_registrados.iterrows():
                c_receta = row_m['CODIGO_RECETA']
                n_receta = row_m['NOMBRE_RECETA']

                coste_produccion = calcular_coste_receta(n_receta)
                pvp_sin_iva = coste_produccion / 0.27 if coste_produccion > 0 else 0.0

                cursor.execute("""
                    SELECT COALESCE(SUM(CANTIDAD), 0.0) FROM movimientos_almacen 
                    WHERE (TIPO = 'SALIDA') AND (CÓDIGO = ? OR PRODUCTO = ?)
                    AND FECHA BETWEEN ? AND ?
                """, (c_receta, n_receta, str_fi, str_ff))
                res_ventas = cursor.fetchone()
                unidades_vendidas = float(res_ventas[0]) if res_ventas else 0.0

                lista_datos_matriz.append({
                    'CODIGO_RECETA': c_receta,
                    'NOMBRE_RECETA': n_receta,
                    'COSTE PRODUCCIÓN €': coste_produccion,
                    'PVP SIN IVA (27% FC) €': pvp_sin_iva,
                    'UNIDADES VENDIDAS': unidades_vendidas
                })

            conn.close()
            df_menu_data = pd.DataFrame(lista_datos_matriz)

            if not df_menu_data.empty:
                def calcular_metricas_menu(row):
                    pvp = float(row['PVP SIN IVA (27% FC) €'])
                    coste = float(row['COSTE PRODUCCIÓN €'])
                    unidades = float(row['UNIDADES VENDIDAS'])
                    
                    mg_contribucion = pvp - coste
                    beneficio_total = mg_contribucion * unidades
                    return pd.Series([mg_contribucion, beneficio_total])

                df_menu_data[['MARGEN CONTRIBUCIÓN €', 'BENEFICIO TOTAL €']] = df_menu_data.apply(calcular_metricas_menu, axis=1)

                avg_mg = df_menu_data['MARGEN CONTRIBUCIÓN €'].mean()
                total_unidades_ventas = df_menu_data['UNIDADES VENDIDAS'].sum()
                num_productos = len(df_menu_data)
                mix_ventas_promedio = (total_unidades_ventas / num_productos) * 0.7 if num_productos > 0 else 0

                def clasificar_plato(row):
                    mg = row['MARGEN CONTRIBUCIÓN €']
                    ventas = row['UNIDADES VENDIDAS']
                    
                    alta_rentabilidad = mg >= avg_mg
                    alta_popularidad = ventas >= mix_ventas_promedio
                    
                    if alta_rentabilidad and alta_popularidad:
                        return "⭐ Estrella"
                    elif not alta_rentabilidad and alta_popularidad:
                        return "🐄 Vaca Lechera"
                    elif alta_rentabilidad and not alta_popularidad:
                        return "❓ Incógnita / Puzzle"
                    else:
                        return "🐶 Perro / Indeseable"

                df_menu_data['CLASIFICACIÓN MENÚ'] = df_menu_data.apply(clasificar_plato, axis=1)

                str_module.markdown(f"### 📊 Matriz de Rentabilidad y Popularidad (Del {fecha_inicio_menu} al {fecha_fin_menu})")
                str_module.info("💡 El **PVP sin IVA** calcula automáticamente el precio recomendado aplicando un objetivo fijo del **27% de Food Cost** sobre el coste de la receta.")
                str_module.dataframe(df_menu_data, use_container_width=True, hide_index=True)

                total_beneficio_menu = df_menu_data['BENEFICIO TOTAL €'].sum()
                col_m1, col_m2, col_m3 = str_module.columns(3)
                with col_m1:
                    str_module.metric("Elaboraciones Analizadas", f"{num_productos}")
                with col_m2:
                    str_module.metric("Margen de Contribución Promedio", f"{avg_mg:.2f} €")
                with col_m3:
                    str_module.metric("Beneficio Bruto Total del Menú", f"{total_beneficio_menu:.2f} €")
            else:
                str_module.info("No hay datos suficientes para calcular la matriz de ingeniería.")
        else:
            str_module.info("Selecciona e incluye elaboraciones en el formulario superior para ver la matriz de ingeniería de menú automatizada.")
    else:
        str_module.info("No hay recetas o elaboraciones registradas.")

with pestana_eventos:
    str_module.title("🎉 Gestión de Eventos y Menús Cerrados")
    str_module.markdown("Registra eventos o menús cerrados, asigna las elaboraciones y cantidades necesarias, y calcula de forma automática los ingredientes totales requeridos frente al stock actual para sumar al pedido.")
    str_module.markdown("---")

    df_recetas_disponibles = ejecutar_sql("SELECT DISTINCT NOMBRE_RECETA FROM recetas_cabecera")

    sub_crear_evento, sub_calculo_evento = str_module.tabs(["➕ Crear / Configurar Evento", "📋 Necesidades de Ingredientes y Pedido"])

    with sub_crear_evento:
        with str_module.form("form_crear_evento"):
            ce_col1, ce_col2, ce_col3 = str_module.columns(3)
            with ce_col1:
                nombre_evento_input = str_module.text_input("Nombre del Evento (Ej: Boda Familia García)")
            with ce_col2:
                fecha_evento_input = str_module.date_input("Fecha del Evento", value=date.today() + timedelta(days=7))
            with ce_col3:
                comensales_input = str_module.number_input("Número de Comensales", min_value=1, value=50)

            str_module.markdown("---")
            str_module.markdown("#### Asociar Elaboración o Plato y Cantidad Total Prevista")

            if not df_recetas_disponibles.empty:
                receta_evento_sel = str_module.selectbox("Seleccionar Elaboración / Receta", df_recetas_disponibles['NOMBRE_RECETA'].tolist())
                cant_unidades_input = str_module.text_input("Cantidad de Raciones / Unidades a Elaborar", value="50")
            else:
                str_module.warning("No hay recetas creadas en el sistema.")
                receta_evento_sel = None
                cant_unidades_input = "0"

            btn_guardar_item_evento = str_module.form_submit_button("💾 Guardar Evento y Añadir Elaboración")

            if btn_guardar_item_evento:
                if not nombre_evento_input.strip():
                    str_module.error("El nombre del evento es obligatorio.")
                elif not receta_evento_sel:
                    str_module.error("Debes seleccionar una receta válida.")
                else:
                    try:
                        cant_unidades_val = float(str(cant_unidades_input).strip().replace(',', '.') or 0.0)
                        fecha_str = fecha_evento_input.strftime("%Y-%m-%d")

                        conn = sqlite3.connect(DB_NAME)
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT OR IGNORE INTO eventos_cabecera (NOMBRE_EVENTO, FECHA_EVENTO, COMENSALES)
                            VALUES (?, ?, ?)
                        """, (nombre_evento_input.strip(), fecha_str, int(comensales_input)))
                        
                        cursor.execute("""
                            UPDATE eventos_cabecera SET COMENSALES = ?, FECHA_EVENTO = ? WHERE NOMBRE_EVENTO = ?
                        """, (int(comensales_input), fecha_str, nombre_evento_input.strip()))

                        cursor.execute("""
                            INSERT INTO eventos_items (NOMBRE_EVENTO, NOMBRE_RECETA, CANTIDAD_UNIDADES)
                            VALUES (?, ?, ?)
                        """, (nombre_evento_input.strip(), receta_evento_sel, cant_unidades_val))

                        conn.commit()
                        conn.close()
                        str_module.success(f"¡Elaboración '{receta_evento_sel}' añadida al evento '{nombre_evento_input.strip()}' con éxito!")
                        str_module.rerun()
                    except Exception as e:
                        str_module.error(f"Error al guardar el evento: {e}")

        str_module.markdown("---")
        str_module.markdown("### 📋 Eventos Registrados Actualmente")
        df_eventos_cab = ejecutar_sql("SELECT * FROM eventos_cabecera")
        if not df_eventos_cab.empty:
            str_module.dataframe(df_eventos_cab, use_container_width=True, hide_index=True)

            opciones_borrar_ev = df_eventos_cab['NOMBRE_EVENTO'].tolist()
            with str_module.form("form_borrar_evento"):
                ev_a_borrar = str_module.selectbox("Selecciona un evento para eliminarlo por completo", opciones_borrar_ev)
                btn_del_ev = str_module.form_submit_button("🗑️ Eliminar Evento Seleccionado")
                if btn_del_ev and ev_a_borrar:
                    try:
                        conn = sqlite3.connect(DB_NAME)
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM eventos_items WHERE NOMBRE_EVENTO = ?", (ev_a_borrar,))
                        cursor.execute("DELETE FROM eventos_cabecera WHERE NOMBRE_EVENTO = ?", (ev_a_borrar,))
                        conn.commit()
                        conn.close()
                        str_module.success(f"¡Evento '{ev_a_borrar}' eliminado correctamente!")
                        str_module.rerun()
                    except Exception as e:
                        str_module.error(f"Error al eliminar: {e}")
        else:
            str_module.info("No hay eventos registrados todavía.")

    with sub_calculo_evento:
        str_module.markdown("### 🛒 Cálculo Automático de Materia Prima Necesaria para Eventos")
        df_eventos_lista = ejecutar_sql("SELECT NOMBRE_EVENTO FROM eventos_cabecera")

        if not df_eventos_lista.empty:
            evento_seleccionado_calculo = str_module.selectbox("Selecciona el Evento a Calcular", df_eventos_lista['NOMBRE_EVENTO'].tolist(), key="sel_ev_calc")

            if evento_seleccionado_calculo:
                df_items_evento = ejecutar_sql("""
                    SELECT NOMBRE_RECETA, CANTIDAD_UNIDADES 
                    FROM eventos_items 
                    WHERE NOMBRE_EVENTO = ?
                """, (evento_seleccionado_calculo,))

                str_module.markdown(f"#### 🍽️ Elaboraciones asociadas al evento: **{evento_seleccionado_calculo}**")
                if not df_items_evento.empty:
                    str_module.dataframe(df_items_evento, use_container_width=True, hide_index=True)

                    ingredientes_necesarios_dict = {}

                    for _, item in df_items_evento.iterrows():
                        nom_receta = item['NOMBRE_RECETA']
                        unidades_a_producir = float(item['CANTIDAD_UNIDADES'])

                        df_ingredientes_receta = ejecutar_sql("""
                            SELECT CODIGO_PRODUCTO, PRODUCTO, CANTIDAD, UNIDAD 
                            FROM recetas_ingredientes 
                            WHERE NOMBRE_RECETA = ?
                        """, (nom_receta,))

                        for _, ing in df_ingredientes_receta.iterrows():
                            cod_prod = ing['CODIGO_PRODUCTO']
                            prod_nombre = ing['PRODUCTO']
                            cant_por_unidad = float(ing['CANTIDAD'])
                            unidad_medida = ing['UNIDAD']

                            cantidad_total_requerida = cant_por_unidad * unidades_a_producir

                            if cod_prod in ingredientes_necesarios_dict:
                                ingredientes_necesarios_dict[cod_prod]['CANTIDAD_TOTAL'] += cantidad_total_requerida
                            else:
                                ingredientes_necesarios_dict[cod_prod] = {
                                    'CÓDIGO': cod_prod,
                                    'PRODUCTO': prod_nombre,
                                    'UNIDAD': unidad_medida,
                                    'CANTIDAD_TOTAL': cantidad_total_requerida
                                }

                    lista_consolidada = []
                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()

                    for cod, datos in ingredientes_necesarios_dict.items():
                        cursor.execute("""
                            SELECT [STOCK ACTUAL EN ALMACÉN], [STOCK MÍNIMO], [PRECIO UNITARIO €] 
                            FROM hoja_almacen WHERE CÓDIGO = ?
                        """, (cod,))
                        res_almacen = cursor.fetchone()

                        stock_actual = float(res_almacen[0]) if res_almacen and res_almacen[0] is not None else 0.0
                        stock_minimo = float(res_almacen[1]) if res_almacen and res_almacen[1] is not None else 0.0
                        precio_unitario = float(res_almacen[2]) if res_almacen and res_almacen[2] is not None else 0.0

                        cant_necesaria_evento = datos['CANTIDAD_TOTAL']

                        cantidad_total_a_pedir = max(0.0, (stock_minimo + cant_necesaria_evento) - stock_actual)
                        coste_pedido_item = cantidad_total_a_pedir * precio_unitario

                        lista_consolidada.append({
                            'CÓDIGO': cod,
                            'PRODUCTO': datos['PRODUCTO'],
                            'UNIDAD': datos['UNIDAD'],
                            'NECESIDAD EVENTO': cant_necesaria_evento,
                            'STOCK ACTUAL': stock_actual,
                            'STOCK MÍNIMO': stock_minimo,
                            'TOTAL A PEDIR (EVENTO + MÍNIMO)': cantidad_total_a_pedir,
                            'COSTE ESTIMADO €': coste_pedido_item
                        })

                    conn.close()
                    df_resultado_final = pd.DataFrame(lista_consolidada)

                    if not df_resultado_final.empty:
                        str_module.markdown("---")
                        str_module.markdown("### 📊 Materia Prima Consolidada para el Evento (Frente al Stock Actual)")
                        str_module.info("💡 La columna **TOTAL A PEDIR (EVENTO + MÍNIMO)** calcula automáticamente la cantidad exacta que debes adquirir sumando lo necesario para el evento más tu stock mínimo de seguridad, descontando el stock actual disponible en el almacén.")
                        str_module.dataframe(df_resultado_final, use_container_width=True, hide_index=True)

                        coste_total_evento_materias = df_resultado_final['COSTE ESTIMADO €'].sum()
                        str_module.markdown(f"### 💰 **Coste Total Estimado de Compra para el Evento:** `{coste_total_evento_materias:.2f} €`")
                    else:
                        str_module.info("No se encontraron ingredientes para las recetas de este evento.")
                else:
                    str_module.info("Este evento no tiene elaboraciones asociadas todavía.")
        else:
            str_module.info("No hay eventos registrados para calcular.")

with pestana_pedidos:
    str_module.title("🛒 Gestión y Emisión de Pedidos a Proveedores")
    str_module.markdown("Genera pedidos automáticos basados en materias primas y programación inteligente de días de pedido por proveedor.")
    str_module.markdown("---")

    df_proveedores = ejecutar_sql("SELECT * FROM proveedores_contactos")
    tab_crear_pedidos, tab_historial_pedidos, tab_contactos = str_module.tabs(["📦 Generar Pedido de Reposición", "📜 Historial de Pedidos", "📇 Agenda de Proveedores"])

    with tab_crear_pedidos:
        str_module.markdown("### Detección de Necesidades por Días de Pedido y Eventos Próximos")
        df_reponer = ejecutar_sql("SELECT PROVEEDOR, CÓDIGO, PRODUCTO, UNIDAD, [STOCK ACTUAL EN ALMACÉN], [STOCK MÍNIMO], [PRECIO UNITARIO €] FROM hoja_almacen")
        
        if not df_reponer.empty:
            def es_materia_prima_valida(row):
                prov = str(row['PROVEEDOR']).upper()
                cod = str(row['CÓDIGO']).upper()
                prod = str(row['PRODUCTO']).upper()
                if "PRODUCCIÓN INTERNA" in prov or "ELAB" in cod or "ELAB" in prod:
                    return False
                return True

            df_reponer_filtrado = df_reponer[df_reponer.apply(es_materia_prima_valida, axis=1)].copy()

            df_eventos_activos = ejecutar_sql("SELECT NOMBRE_EVENTO, FECHA_EVENTO FROM eventos_cabecera")
            necesidades_eventos_dict = {}
            if not df_eventos_activos.empty:
                dias_nieves_str = "LUNES, VIERNES"
                df_prov_nieves = ejecutar_sql("SELECT DIAS_PEDIDO FROM proveedores_contactos WHERE NOMBRE_PROVEEDOR = 'NIEVES'")
                if not df_prov_nieves.empty and pd.notna(df_prov_nieves.iloc[0]['DIAS_PEDIDO']):
                    dias_nieves_str = str(df_prov_nieves.iloc[0]['DIAS_PEDIDO'])
                
                def obtener_fecha_pedido_mas_cercana(fecha_evento_str, dias_str):
                    try:
                        f_evento = datetime.strptime(fecha_evento_str, "%Y-%m-%d").date()
                    except:
                        return None
                    map_dias = {'LUNES': 0, 'MARTES': 1, 'MIERCOLES': 2, 'MIÉRCOLES': 2, 'JUEVES': 3, 'VIERNES': 4, 'SABADO': 5, 'SÁBADO': 5, 'DOMINGO': 6}
                    dias_habiles = []
                    for d in dias_str.split(','):
                        d_clean = d.strip().upper()
                        if d_clean in map_dias:
                            dias_habiles.append(map_dias[d_clean])
                    if not dias_habiles:
                        dias_habiles = [0, 4]
                    current_date = f_evento
                    for _ in range(14):
                        if current_date.weekday() in dias_habiles:
                            return current_date
                        current_date -= timedelta(days=1)
                    return f_evento

                hoy = date.today()
                for _, ev in df_eventos_activos.iterrows():
                    nom_ev = ev['NOMBRE_EVENTO']
                    fecha_ev_str = ev['FECHA_EVENTO']
                    try:
                        f_ev_date = datetime.strptime(fecha_ev_str, "%Y-%m-%d").date()
                    except:
                        continue
                    
                    if f_ev_date < hoy:
                        continue
                    
                    f_pedido_cercana = obtener_fecha_pedido_mas_cercana(fecha_ev_str, dias_nieves_str)
                    if f_pedido_cercana and hoy >= f_pedido_cercana:
                        df_items_ev = ejecutar_sql("SELECT NOMBRE_RECETA, CANTIDAD_UNIDADES FROM eventos_items WHERE NOMBRE_EVENTO = ?", (nom_ev,))
                        for _, it in df_items_ev.iterrows():
                            n_rec = it['NOMBRE_RECETA']
                            cant_un = float(it['CANTIDAD_UNIDADES'])
                            df_ings = ejecutar_sql("SELECT CODIGO_PRODUCTO, CANTIDAD FROM recetas_ingredientes WHERE NOMBRE_RECETA = ?", (n_rec,))
                            for _, ing in df_ings.iterrows():
                                c_prod = ing['CODIGO_PRODUCTO']
                                c_cant = float(ing['CANTIDAD']) * cant_un
                                necesidades_eventos_dict[c_prod] = necesidades_eventos_dict.get(c_prod, 0.0) + c_cant

            def calcular_necesidad_total(row):
                s = float(row['STOCK ACTUAL EN ALMACÉN']) if pd.notna(row['STOCK ACTUAL EN ALMACÉN']) else 0.0
                m = float(row['STOCK MÍNIMO']) if pd.notna(row['STOCK MÍNIMO']) else 0.0
                cod = row['CÓDIGO']
                nec_ev = necesidades_eventos_dict.get(cod, 0.0)
                return max(0.0, (m + nec_ev) - s)

            df_reponer_filtrado['CANTIDAD A PEDIR'] = df_reponer_filtrado.apply(calcular_necesidad_total, axis=1)
            df_pendientes = df_reponer_filtrado[df_reponer_filtrado['CANTIDAD A PEDIR'] > 0]

            if not df_pendientes.empty:
                proveedores_lista = df_pendientes['PROVEEDOR'].unique().tolist()
                prov_seleccionado = str_module.selectbox("Filtrar pedido por Proveedor", proveedores_lista, key="select_prov_pedido")

                dias_prov_str = "No especificados"
                if not df_proveedores.empty:
                    m_prov = df_proveedores[df_proveedores['NOMBRE_PROVEEDOR'] == prov_seleccionado]
                    if not m_prov.empty and 'DIAS_PEDIDO' in m_prov.columns and pd.notna(m_prov.iloc[0]['DIAS_PEDIDO']):
                        dias_prov_str = m_prov.iloc[0]['DIAS_PEDIDO']
                
                str_module.markdown(f"📅 **Días de Pedido Hábiles para {prov_seleccionado}:** `{dias_prov_str}`")

                df_pedido_prov = df_pendientes[df_pendientes['PROVEEDOR'] == prov_seleccionado]
                str_module.dataframe(df_pedido_prov, use_container_width=True, hide_index=True)

                detalle_texto = ""
                coste_estimado_pedido = 0.0
                for _, row in df_pedido_prov.iterrows():
                    cant = row['CANTIDAD A PEDIR']
                    prod = row['PRODUCTO']
                    uni = row['UNIDAD']
                    precio = row['PRECIO UNITARIO €'] if pd.notna(row['PRECIO UNITARIO €']) else 0.0
                    coste_estimado_pedido += cant * precio
                    detalle_texto += f"- {cant} {uni} de {prod}\n"

                mensaje_wats_default = f"Hola, buenos días. Necesitamos realizar el siguiente pedido para la cocina:\n\n{detalle_texto}\nGracias y un saludo."

                str_module.markdown("---")
                str_module.markdown("### 💬 Previsualización del Pedido antes de Generar")
                str_module.info("Revisa el texto. Al pulsar el botón, el pedido se guardará en el historial como **PENDIENTE** y se habilitará el enlace de envío.")

                mensaje_editado = str_module.text_area("Mensaje para el Proveedor", value=mensaje_wats_default, height=150)
                str_module.markdown(f"**Coste estimado del pedido:** `{coste_estimado_pedido:.2f} €`")

                if str_module.button("🚀 Volcar Pedido como PENDIENTE y Preparar Envío"):
                    try:
                        forma_envio = "WhatsApp"
                        correo_prov = ""
                        telefono_prov = ""

                        if not df_proveedores.empty:
                            match_prov = df_proveedores[df_proveedores['NOMBRE_PROVEEDOR'] == prov_seleccionado]
                            if not match_prov.empty:
                                if pd.notna(match_prov.iloc[0]['FORMA_ENVIO']):
                                    forma_envio = str(match_prov.iloc[0]['FORMA_ENVIO']).strip()
                                if pd.notna(match_prov.iloc[0]['CORREO']):
                                    correo_prov = str(match_prov.iloc[0]['CORREO']).strip()
                                if pd.notna(match_prov.iloc[0]['TELEFONO']):
                                    telefono_prov = str(match_prov.iloc[0]['TELEFONO']).strip()

                        num_pedido_gen = f"PED-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                        fecha_ped = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        conn = sqlite3.connect(DB_NAME)
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO historial_pedidos (NUMERO_PEDIDO, FECHA, PROVEEDOR, DETALLE_PEDIDO, COSTE_TOTAL, ESTADO)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (num_pedido_gen, fecha_ped, prov_seleccionado, mensaje_editado, coste_estimado_pedido, "PENDIENTE"))
                        conn.commit()
                        conn.close()

                        str_module.success("¡Pedido registrado en el historial como PENDIENTE con éxito!")

                        if "EMAIL" in forma_envio.upper():
                            asunto_email = urllib.parse.quote(f"Nuevo Pedido - {num_pedido_gen}")
                            cuerpo_email = urllib.parse.quote(mensaje_editado)
                            link_email = f"mailto:{correo_prov}?subject={asunto_email}&body={cuerpo_email}"
                            str_module.markdown(f"[📧 Haz clic aquí para Enviar el Pedido por Correo Electrónico]({link_email})", unsafe_allow_html=True)
                        else:
                            encoded_msg = urllib.parse.quote(mensaje_editado)
                            link_whatsapp = f"https://wa.me/{telefono_prov}?text={encoded_msg}" if telefono_prov else f"https://wa.me/?text={encoded_msg}"
                            str_module.markdown(f"[📲 Haz clic aquí para Enviar el Pedido por WhatsApp]({link_whatsapp})", unsafe_allow_html=True)

                    except Exception as e:
                        str_module.error(f"Error al registrar el pedido: {e}")
            else:
                str_module.info("¡Enhorabuena! No hay ninguna materia prima por debajo del stock mínimo ni requerida por eventos en este momento.")
        else:
            str_module.info("No hay referencias en el inventario.")

    with tab_historial_pedidos:
        str_module.markdown("### 📜 Historial de Pedidos Realizados")
        
        col_p1, col_p2 = str_module.columns(2)
        with col_p1:
            fecha_inicio_ped = str_module.date_input("Fecha Inicio Pedidos", value=date.today() - timedelta(days=30), key="ped_fi")
        with col_p2:
            fecha_fin_ped = str_module.date_input("Fecha Fin Pedidos", value=date.today(), key="ped_ff")

        str_fip = fecha_inicio_ped.strftime("%Y-%m-%d")
        str_ffp = fecha_fin_ped.strftime("%Y-%m-%d 23:59:59")

        df_hist_pedidos = ejecutar_sql("""
            SELECT * FROM historial_pedidos 
            WHERE FECHA BETWEEN ? AND ? 
            ORDER BY ID DESC
        """, (str_fip, str_ffp))
        
        if not df_hist_pedidos.empty:
            coste_total_acumulado = df_hist_pedidos['COSTE_TOTAL'].sum()
            total_pedidos_count = len(df_hist_pedidos)
            
            df_facturables = df_hist_pedidos[df_hist_pedidos['ESTADO'] != 'ANULADO']
            coste_facturable = df_facturables['COSTE_TOTAL'].sum()

            col_met1, col_met2, col_met3 = str_module.columns(3)
            with col_met1:
                str_module.metric("Total Pedidos en Periodo", f"{total_pedidos_count}")
            with col_met2:
                str_module.metric("Coste Global del Periodo", f"{coste_total_acumulado:.2f} €")
            with col_met3:
                str_module.metric("Coste Real (Sin Anulados)", f"{coste_facturable:.2f} €")

            str_module.markdown("---")
            str_module.dataframe(df_hist_pedidos, use_container_width=True, hide_index=True)
            
            str_module.markdown("---")
            str_module.markdown("### 🔄 Gestión de Pedido: Actualizar, Modificar o Anular")
            with str_module.form("form_gestion_pedido"):
                col_up1, col_up2, col_up3, col_up4 = str_module.columns(4)
                with col_up1:
                    pedidos_lista = df_hist_pedidos['NUMERO_PEDIDO'].tolist()
                    ped_sel = str_module.selectbox("Número de Pedido", pedidos_lista)
                with col_up2:
                    nuevo_estado = str_module.selectbox("Acción / Nuevo Estado", ["PENDIENTE", "ENVIADO", "RECIBIDO", "MODIFICADO", "ANULADO"])
                with col_up3:
                    nuevo_coste_input = str_module.text_input("Nuevo Coste (€)", value="0.0")
                with col_up4:
                    str_module.markdown("<br>", unsafe_allow_html=True)
                    btn_gestionar_ped = str_module.form_submit_button("⚡ Aplicar Cambios al Pedido")
                
                nuevo_detalle_input = str_module.text_area("Modificar Detalle del Pedido (Opcional)", value="", height=80)

                if btn_gestionar_ped and ped_sel:
                    try:
                        coste_parseado = float(str(nuevo_coste_input).strip().replace(',', '.') or 0.0)
                        conn = sqlite3.connect(DB_NAME)
                        cursor = conn.cursor()
                        
                        if nuevo_detalle_input.strip():
                            cursor.execute("""
                                UPDATE historial_pedidos 
                                SET ESTADO = ?, COSTE_TOTAL = CASE WHEN ? > 0 THEN ? ELSE COSTE_TOTAL END, DETALLE_PEDIDO = ? 
                                WHERE NUMERO_PEDIDO = ?
                            """, (nuevo_estado, coste_parseado, coste_parseado, nuevo_detalle_input, ped_sel))
                        else:
                            cursor.execute("""
                                UPDATE historial_pedidos 
                                SET ESTADO = ?, COSTE_TOTAL = CASE WHEN ? > 0 THEN ? ELSE COSTE_TOTAL END 
                                WHERE NUMERO_PEDIDO = ?
                            """, (nuevo_estado, coste_parseado, coste_parseado, ped_sel))
                            
                        conn.commit()
                        conn.close()
                        str_module.success(f"¡El pedido {ped_sel} ha sido actualizado correctamente (Estado: {nuevo_estado})!")
                        str_module.rerun()
                    except Exception as e:
                        str_module.error(f"Error al actualizar el pedido: {e}")
        else:
            str_module.info("No hay historial de pedidos registrado en el rango de fechas seleccionado.")

    with tab_contactos:
        str_module.markdown("### 📇 Agenda y Contactos de Proveedores")
        
        with str_module.form("form_nuevo_proveedor"):
            cp1, cp2, cp3 = str_module.columns(3)
            with cp1:
                nom_prov_input = str_module.text_input("Nombre del Proveedor")
                contacto_prov_input = str_module.text_input("Persona de Contacto")
            with cp2:
                tel_prov_input = str_module.text_input("Teléfono / WhatsApp (Ej: 34600000000)")
                correo_prov_input = str_module.text_input("Correo Electrónico")
            with cp3:
                envio_prov_input = str_module.selectbox("Forma de Envío Habitual", ["WhatsApp", "Correo Electrónico"])
                dias_prov_input = str_module.text_input("Días de Pedido (Ej: LUNES, JUEVES)", value="LUNES, VIERNES")
                
            btn_guardar_prov = str_module.form_submit_button("💾 Guardar Proveedor en Agenda")
            
            if btn_guardar_prov and nom_prov_input.strip():
                try:
                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR REPLACE INTO proveedores_contactos 
                        (NOMBRE_PROVEEDOR, CONTACTO, TELEFONO, CORREO, FORMA_ENVIO, DIAS_PEDIDO)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (nom_prov_input.strip(), contacto_prov_input, tel_prov_input, correo_prov_input, envio_prov_input, dias_prov_input))
                    conn.commit()
                    conn.close()
                    str_module.success(f"¡Proveedor '{nom_prov_input.strip()}' guardado correctamente!")
                    str_module.rerun()
                except Exception as e:
                    str_module.error(f"Error al guardar proveedor: {e}")

        str_module.markdown("---")
        df_agenda = ejecutar_sql("SELECT * FROM proveedores_contactos")
        if not df_agenda.empty:
            str_module.dataframe(df_agenda, use_container_width=True, hide_index=True)
        else:
            str_module.info("No hay proveedores registrados en la agenda.")

with pestana_facturacion:
    str_module.title("📑 Facturación y Gestoría")
    str_module.markdown("Control de ingresos, registros contables y documentación para gestoría.")
    str_module.markdown("---")

    tab_ingresos, tab_gestoria_docs, tab_conciliacion = str_module.tabs(["💵 Registro de Ingresos", "📂 Documentos y Gestoría", "🔍 Conciliación Albaranes / Facturas"])

    with tab_ingresos:
        str_module.markdown("### 📊 Control de Ingresos y Facturación")
        with str_module.form("form_nuevo_ingreso"):
            c_i1, c_i2, c_i3 = str_module.columns(3)
            with c_i1:
                fecha_ingreso = str_module.date_input("Fecha", value=date.today())
                concepto_ingreso = str_module.text_input("Concepto / Descripción")
            with c_i2:
                categoria_ingreso = str_module.selectbox("Categoría", ["Restaurante / Sala", "Eventos", "Take Away / Delivery", "Otros"])
                base_imponible = str_module.text_input("Base Imponible (€)", value="0.0")
            with c_i3:
                tipo_iva = str_module.selectbox("Tipo IVA (%)", [10.0, 21.0, 4.0, 0.0])
                str_module.markdown("<br>", unsafe_allow_html=True)
                btn_guardar_ingreso = str_module.form_submit_button("💾 Guardar Ingreso")

            if btn_guardar_ingreso:
                try:
                    bi = float(str(base_imponible).strip().replace(',', '.') or 0.0)
                    total_calculado = bi * (1.0 + (tipo_iva / 100.0))
                    f_str = fecha_ingreso.strftime("%Y-%m-%d")

                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO facturacion_ingresos (FECHA, CONCEPTO, CATEGORIA, BASE_IMPONIBLE, TIPO_IVA, TOTAL)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (f_str, concepto_ingreso, categoria_ingreso, bi, tipo_iva, total_calculado))
                    conn.commit()
                    conn.close()

                    str_module.success("¡Ingreso registrado correctamente!")
                    str_module.rerun()
                except Exception as e:
                    str_module.error(f"Error al registrar ingreso: {e}")

        str_module.markdown("---")
        df_ingresos = ejecutar_sql("SELECT * FROM facturacion_ingresos ORDER BY ID DESC")
        if not df_ingresos.empty:
            total_facturado = df_ingresos['TOTAL'].sum()
            total_base = df_ingresos['BASE_IMPONIBLE'].sum()
            str_module.metric("Total Facturación Acumulada", f"{total_facturado:.2f} €", f"Base: {total_base:.2f} €")
            str_module.dataframe(df_ingresos, use_container_width=True, hide_index=True)
        else:
            str_module.info("No hay registros de ingresos todavía.")

    with tab_gestoria_docs:
        str_module.markdown("### 📂 Documentación para Gestoría y Trámites")
        with str_module.form("form_nuevo_doc_gestoria"):
            cg_1, cg_2, cg_3 = str_module.columns(3)
            with cg_1:
                fecha_doc = str_module.date_input("Fecha Documento", value=date.today(), key="doc_f")
                tipo_doc = str_module.selectbox("Tipo de Documento", ["Impuestos (IVA / IRPF)", "Nomina / Seguros Sociales", "Licencia / Sanidad", "Factura Proveedor", "Otro"])
            with cg_2:
                desc_doc = str_module.text_input("Descripción / Observaciones")
                estado_doc = str_module.selectbox("Estado", ["Pendiente", "Enviado a Gestoría", "Completado / Archivo"])
            with cg_3:
                importe_doc = str_module.text_input("Importe asociado (€)", value="0.0")
                str_module.markdown("<br>", unsafe_allow_html=True)
                btn_guardar_doc = str_module.form_submit_button("💾 Registrar Documento")

            if btn_guardar_doc:
                try:
                    imp = float(str(importe_doc).strip().replace(',', '.') or 0.0)
                    f_str_d = fecha_doc.strftime("%Y-%m-%d")

                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO gestoria_documentos (FECHA, TIPO, DESCRIPCION, ESTADO, IMPORTE)
                        VALUES (?, ?, ?, ?, ?)
                    """, (f_str_d, tipo_doc, desc_doc, estado_doc, imp))
                    conn.commit()
                    conn.close()

                    str_module.success("¡Documento registrado correctamente para gestoría!")
                    str_module.rerun()
                except Exception as e:
                    str_module.error(f"Error al registrar documento: {e}")

        str_module.markdown("---")
        df_docs = ejecutar_sql("SELECT * FROM gestoria_documentos ORDER BY ID DESC")
        if not df_docs.empty:
            str_module.dataframe(df_docs, use_container_width=True, hide_index=True)
        else:
            str_module.info("No hay documentos registrados para gestoría.")

    with tab_conciliacion:
        str_module.markdown("### 🔍 Conciliación de Albaranes y Facturas por Proveedor")

        with str_module.form("form_registrar_albaran_factura"):
            ca1, ca2, ca3 = str_module.columns(3)
            with ca1:
                prov_alb = str_module.text_input("Proveedor")
                num_ped_rel = str_module.text_input("Nº Pedido Relacionado (Opcional)")
            with ca2:
                num_alb = str_module.text_input("Nº de Albarán")
                importe_alb = str_module.text_input("Importe del Albarán (€)", value="0.0")
            with ca3:
                tiene_fac = str_module.selectbox("¿Tiene Factura Asociada?", ["NO", "SI"])
                num_fac_rel = str_module.text_input("Nº de Factura (si la tiene)")
                
            btn_guardar_alb = str_module.form_submit_button("📥 Registrar Albarán y Verificar Estado")
            
            if btn_guardar_alb:
                try:
                    imp_val = float(str(importe_alb).strip().replace(',', '.') or 0.0)
                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR REPLACE INTO control_albaranes_facturas 
                        (FECHA, PROVEEDOR, NUMERO_PEDIDO, NUMERO_ALBARAN, IMPORTE_ALBARAN, TIENE_FACTURA, NUMERO_FACTURA)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (date.today().strftime("%Y-%m-%d"), prov_alb, num_ped_rel, num_alb, imp_val, tiene_fac, num_fac_rel))
                    conn.commit()
                    conn.close()
                    str_module.success("¡Albarán registrado correctamente en el sistema de control!")
                    str_module.rerun()
                except Exception as e:
                    str_module.error(f"Error al registrar: {e}")

        str_module.markdown("---")
        str_module.markdown("### 📋 Albaranes Pendientes de Factura")

        df_control_alb = ejecutar_sql("SELECT * FROM control_albaranes_facturas ORDER BY FECHA DESC")
        if not df_control_alb.empty:
            df_faltan_factura = df_control_alb[df_control_alb['TIENE_FACTURA'] == 'NO']
            
            if not df_faltan_factura.empty:
                str_module.warning(f"⚠️ Se han detectado {len(df_faltan_factura)} albaranes pendientes de recibir o asociar su factura correspondiente.")
                str_module.dataframe(df_faltan_factura, use_container_width=True, hide_index=True)
            else:
                str_module.success("✅ Todos los albaranes registrados tienen su factura asociada correctamente.")
                
            str_module.markdown("#### Histórico General de Albaranes")
            str_module.dataframe(df_control_alb, use_container_width=True, hide_index=True)
        else:
            str_module.info("No hay albaranes registrados todavía para analizar.")
