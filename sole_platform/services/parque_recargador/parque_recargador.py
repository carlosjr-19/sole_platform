import pandas as pd
import os
import uuid
from datetime import datetime

def process_parque_recargador_csv(file_path):
    try:
        archivo = pd.read_csv(file_path)
    except Exception as e:
        return {"error": f"Error al leer el archivo CSV: {str(e)}"}

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
    parque_por_marca = parque_por_marca_df.to_dict('records')

    # 5. Paquetes más recargados en general (usando altan_name)
    paquetes_populares_df = archivo['altan_name'].value_counts().reset_index()
    paquetes_populares_df.columns = ['Paquete', 'Total Recargas']
    paquetes_populares = paquetes_populares_df.to_dict('records')
    total_paquetes = int(archivo['altan_name'].value_counts().sum())

    # 6. Ingreso por recargas totales de cada marca con el precio de referencia (mvno_price)
    precios_por_nombre_df = archivo.groupby('name')['mvno_price'].sum().reset_index()
    precios_por_nombre_df.columns = ['Marca', 'Ingreso']
    precios_por_nombre_df['Ingreso'] = precios_por_nombre_df['Ingreso'].round(2)
    precios_por_nombre = precios_por_nombre_df.to_dict('records')

    # 7. Total que se le paga altan por precio de referencia
    total_altan = round(0.65 * precio_r, 2)

    # 8. Total que se le paga altan por líneas en parque recargador
    total_parque = round(parque_r * 5, 2)

    # 9. Total a pagar a ALTAN
    total = round(total_altan + total_parque, 2)

    # 10. Ganancias del mes por recargas
    ganancia = round(precio_m - total, 2)

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
        'ganancia_mes': ganancia
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
            'Pago a ALTAN por Ref (65%)',
            'Pago a ALTAN por Parque',
            'Total a Pagar a ALTAN',
            'Ganancias del Mes'
        ],
        'Valor': [
            resultados['precio_r'],
            resultados['precio_m'],
            resultados['total_recargas'],
            resultados['parque_r'],
            resultados['total_altan'],
            resultados['total_parque'],
            resultados['total_pagar_altan'],
            resultados['ganancia_mes']
        ]
    }
    df_resumen = pd.DataFrame(resumen_data)

    # 2. Parque Recargador por Marca
    df_parque = pd.DataFrame(resultados['parque_por_marca'])

    # 3. Recargas Totales por Marca
    df_recargas = pd.DataFrame(resultados['recargas_por_marca'])

    # 4. Ingreso por Marca
    df_ingresos = pd.DataFrame(resultados['precios_por_nombre'])

    # 5. Paquetes (altan_name)
    df_paquetes = pd.DataFrame(resultados['paquetes_populares'])

    # Guardar en Excel
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"reporte_parque_recargador_{timestamp}.xlsx"
    filepath = os.path.join(download_folder, filename)

    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
        df_parque.to_excel(writer, sheet_name='Parque por Marca', index=False)
        df_recargas.to_excel(writer, sheet_name='Recargas por Marca', index=False)
        df_ingresos.to_excel(writer, sheet_name='Ingreso por Marca', index=False)
        df_paquetes.to_excel(writer, sheet_name='Paquetes', index=False)
        
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
