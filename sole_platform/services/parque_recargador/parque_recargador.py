import pandas as pd
import os
import uuid
from datetime import datetime

def process_parque_recargador_csv(file_path, comisiones_path=None, anio=None, portabilidades_path=None):
    try:
        archivo = pd.read_csv(file_path)
    except Exception as e:
        return {"error": f"Error al leer el archivo CSV: {str(e)}"}

    # Filtrar msisdn que comiencen con 1
    if 'msisdn' in archivo.columns:
        archivo['msisdn'] = archivo['msisdn'].astype(str)
        archivo = archivo[~archivo['msisdn'].str.startswith('1')]

    # Cargar comisiones si están disponibles
    comisiones_dict = {}
    if comisiones_path and anio:
        try:
            df_comisiones = pd.read_excel(comisiones_path, sheet_name=str(anio))
            if 'CLIENTE' in df_comisiones.columns and 'TOTAL' in df_comisiones.columns:
                for index, row in df_comisiones.iterrows():
                    cliente = str(row['CLIENTE']).strip().lower()
                    if pd.notna(row['TOTAL']) and cliente != 'total' and cliente != 'nan':
                        comisiones_dict[cliente] = float(row['TOTAL'])
        except Exception as e:
            print(f"Error procesando archivo de comisiones: {e}")

    # Cargar portabilidades si están disponibles
    portabilidades_dict = {}
    if portabilidades_path:
        try:
            df_port = pd.read_excel(portabilidades_path)
            if 'Marca' in df_port.columns and 'Portabilidades_Exitosas' in df_port.columns and 'Costo_Total_MXN' in df_port.columns:
                for index, row in df_port.iterrows():
                    marca_str = str(row['Marca']).strip().lower()
                    if marca_str != 'nan':
                        val = row['Costo_Total_MXN']
                        if isinstance(val, str):
                            val = val.replace('$', '').replace(' ', '')
                            last_comma = val.rfind(',')
                            last_dot = val.rfind('.')
                            if last_comma > last_dot:
                                val = val.replace('.', '').replace(',', '.')
                            elif ',' in val:
                                val = val.replace(',', '')
                        costo = float(val) if pd.notna(val) and val != '' else 0.0
                        cantidad = int(row['Portabilidades_Exitosas']) if pd.notna(row['Portabilidades_Exitosas']) else 0
                        portabilidades_dict[marca_str] = {
                            'cantidad': cantidad,
                            'costo': costo
                        }
        except Exception as e:
            print(f"Error procesando archivo de portabilidades: {e}")

    # Asegurar que existan las columnas necesarias, si no, usar valores por defecto o fallar con gracia
    if 'altan_name' not in archivo.columns:
        if 'mvno_package_name' in archivo.columns:
            archivo['altan_name'] = archivo['mvno_package_name']
        else:
            return {"error": "El archivo no contiene la columna 'altan_name' ni 'mvno_package_name'."}

    # 1. Ingreso totales de recargas con el precio de referencia ALTAN
    precio_r = round(archivo['price'].sum(), 2)

    # 2. Ingreso totales de recargas con el precio de mvno
    precio_m = round(archivo['mvno_price'].sum(), 2)

    # 3. Recargas totales por marca
    recargas_por_marca_df = archivo['name'].value_counts().reset_index()
    recargas_por_marca_df.columns = ['Marca', 'Total Recargas']
    recargas_por_marca = recargas_por_marca_df.to_dict('records')
    total_recargas = int(archivo['name'].value_counts().sum())

    # 4. Parque recargador por marca
    n_archivo = archivo.drop_duplicates('msisdn')
    parque_r = int(n_archivo['name'].value_counts().sum())
    
    parque_por_marca_df = n_archivo['name'].value_counts().reset_index()
    parque_por_marca_df.columns = ['Marca', 'Parque Recargador']
    
    # Agregar porcentaje
    if parque_r > 0:
        parque_por_marca_df['Porcentaje (%)'] = (parque_por_marca_df['Parque Recargador'] / parque_r) * 100
        parque_por_marca_df['Porcentaje (%)'] = parque_por_marca_df['Porcentaje (%)'].round(2)
    else:
        parque_por_marca_df['Porcentaje (%)'] = 0.0

    parque_por_marca = parque_por_marca_df.to_dict('records')

    # 5. Paquetes más recargados en general (usando altan_name)
    paquetes_populares_df = archivo['altan_name'].value_counts().reset_index()
    paquetes_populares_df.columns = ['Paquete', 'Total Recargas']
    paquetes_populares = paquetes_populares_df.to_dict('records')
    total_paquetes = int(archivo['altan_name'].value_counts().sum())

    # 6. Ingreso por recargas totales de cada marca con el precio de referencia (mvno_price)
    # Suma de altan_price por marca
    altan_price_por_nombre = archivo.groupby('name')['altan_price'].sum().to_dict() if 'altan_price' in archivo.columns else {}

    # 6. Ingreso por recargas totales de cada marca con el precio de referencia (mvno_price)
    precios_por_nombre_df = archivo.groupby('name')['mvno_price'].sum().reset_index()
    precios_por_nombre_df.columns = ['Marca', 'Ingreso']
    
    def calcular_finanzas_marca(row):
        ingreso = row['Ingreso']
        marca = row['Marca']
        marca_lower = str(marca).strip().lower()
        
        comision = comisiones_dict.get(marca_lower, 0.0)
        ganancia_bruta = ingreso - comision
        
        pago_altan = altan_price_por_nombre.get(marca, 0.0)
        port_info = portabilidades_dict.get(marca_lower, {'cantidad': 0, 'costo': 0.0})
        port_cantidad = port_info['cantidad']
        port_costo = port_info['costo']
        
        ganancia_neta = ganancia_bruta - pago_altan - port_costo
        margen = (ganancia_neta / ingreso) * 100 if ingreso > 0 else 0.0
        
        port_str = f"{port_cantidad} (-${port_costo:,.2f})" if port_cantidad > 0 or port_costo > 0 else "0 (-$0.00)"
        
        return pd.Series([comision, ganancia_bruta, pago_altan, port_str, port_costo, ganancia_neta, margen])
        
    precios_por_nombre_df[['Comision', 'Ganancia Bruta', 'Pago Altan', 'Portabilidades Str', 'Portabilidades Costo', 'Ganancia Neta', 'Margen (%)']] = precios_por_nombre_df.apply(calcular_finanzas_marca, axis=1)
    
    precios_por_nombre_df['Ingreso'] = precios_por_nombre_df['Ingreso'].round(2)
    precios_por_nombre_df['Comision'] = precios_por_nombre_df['Comision'].round(2)
    precios_por_nombre_df['Ganancia Bruta'] = precios_por_nombre_df['Ganancia Bruta'].round(2)
    precios_por_nombre_df['Pago Altan'] = precios_por_nombre_df['Pago Altan'].round(2)
    precios_por_nombre_df['Ganancia Neta'] = precios_por_nombre_df['Ganancia Neta'].round(2)
    precios_por_nombre_df['Margen (%)'] = precios_por_nombre_df['Margen (%)'].round(2)
    
    precios_por_nombre = precios_por_nombre_df.to_dict('records')
    
    margen_por_marca_df = precios_por_nombre_df[['Marca', 'Margen (%)']].sort_values(by='Margen (%)', ascending=False)
    margen_por_marca = margen_por_marca_df.to_dict('records')

    # 7. Total que se le paga altan por precio de referencia
    total_altan = round(0.65 * precio_r, 2)

    # 8. Total que se le paga altan por líneas en parque recargador
    total_parque = round(parque_r * 5, 2)

    # 9. Total a pagar a ALTAN
    total = round(total_altan + total_parque, 2)

    # 10. Total comisiones
    total_comisiones = sum(comisiones_dict.values())
    total_comisiones = round(total_comisiones, 2)

    # 11. Ganancias del mes por recargas
    ganancia_bruta_total = round(precios_por_nombre_df['Ganancia Bruta'].sum(), 2)
    ganancia_neta_total = round(precios_por_nombre_df['Ganancia Neta'].sum(), 2)

    return {
        'precio_r': precio_r,
        'precio_m': precio_m,
        'recargas_por_marca': recargas_por_marca,
        'total_recargas': total_recargas,
        'parque_por_marca': parque_por_marca,
        'parque_r': parque_r,
        'paquetes_populares': paquetes_populares,
        'total_paquetes': total_paquetes,
        'precios_por_nombre': precios_por_nombre,
        'total_altan': total_altan,
        'total_parque': total_parque,
        'total_pagar_altan': total,
        'total_comisiones': total_comisiones,
        'ganancia_bruta': ganancia_bruta_total,
        'ganancia_mes': ganancia_neta_total,
        'margen_por_marca': margen_por_marca
    }

def generar_excel_parque(resultados, download_folder):
    """
    Genera un archivo de Excel con 5 hojas basado en los resultados obtenidos del CSV.
    """
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Crear dataframes para las hojas
    # 1. Resumen
    resumen_data = {
        'Métrica': [
            'Ingreso Total (Precio Referencia ALTAN)',
            'Ingreso Total (Precio MVNO)',
            'Total de Recargas Realizadas',
            'Total Parque Recargador (Líneas)',
            'Pago a ALTAN por Parque',
            'Total a Pagar a ALTAN',
            'Total Comisiones Pagadas',
            'Ganancia Bruta Total',
            'Ganancia Neta Total'
        ],
        'Valor': [
            resultados['precio_r'],
            resultados['precio_m'],
            resultados['total_recargas'],
            resultados['parque_r'],
            resultados['total_parque'],
            resultados['total_pagar_altan'],
            resultados['total_comisiones'],
            resultados['ganancia_bruta'],
            resultados['ganancia_mes']
        ]
    }
    df_resumen = pd.DataFrame(resumen_data)

    # 2. Parque Recargador por Marca
    df_parque = pd.DataFrame(resultados['parque_por_marca'])

    # 3. Recargas Totales por Marca
    df_recargas = pd.DataFrame(resultados['recargas_por_marca'])

    # 4. Ingreso por Marca
    # 4. Ingreso y Ganancia por Marca
    df_ingresos = pd.DataFrame(resultados['precios_por_nombre'])
    # Reordenar o limpiar columnas para mostrar en Excel
    df_ingresos_export = df_ingresos[['Marca', 'Ingreso', 'Comision', 'Ganancia Bruta', 'Pago Altan', 'Portabilidades Str', 'Ganancia Neta', 'Margen (%)']].copy()
    df_ingresos_export.rename(columns={'Portabilidades Str': 'Portabilidades'}, inplace=True)

    # 5. Margen por Marca
    df_margen = pd.DataFrame(resultados['margen_por_marca'])

    # Guardar en Excel
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"reporte_parque_recargador_{timestamp}.xlsx"
    filepath = os.path.join(download_folder, filename)

    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
        df_parque.to_excel(writer, sheet_name='Parque por Marca', index=False)
        df_recargas.to_excel(writer, sheet_name='Recargas por Marca', index=False)
        df_ingresos_export.to_excel(writer, sheet_name='Ingreso y Ganancia', index=False)
        df_margen.to_excel(writer, sheet_name='Margen de Ganancia', index=False)
        
        # Ajustar ancho de columnas automáticamente si es posible
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column].width = adjusted_width

    return filename
