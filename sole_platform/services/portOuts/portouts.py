import os
import json
import polars as pl
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows 
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account

SPREADSHEET_ID = '11LZkRNehJykY2DKwmTC856h-vdMT1YLX4lDkHMtvs0Q'

def get_connection():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    creds_dict = json.loads(creds_json)
    
    try:
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds, static_discovery=False)
    except Exception as e:
        print(f"Error crítico al parsear GOOGLE_CREDENTIALS_JSON: {e}")
        DISCOVERY_SERVICE_URL = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
        service = build('sheets', 'v4', credentials=creds, discoveryServiceUrl=DISCOVERY_SERVICE_URL, static_discovery=False)

    service = build('sheets', 'v4', credentials=creds, static_discovery=False)
    
    sheet = service.spreadsheets()


    return sheet

def lista_mvnos():
    try:
        sheet = get_connection()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='PORT OUT GUI').execute()
        values = result.get('values', [])

        if not values:
            return []

        # Buscar índice de columna "Marca" o "MVNO"
        headers = [str(h).strip().upper() for h in values[0]]
        target_headers = ["MARCA"]
        
        col_index = next((i for i, h in enumerate(headers) if h in target_headers), -1)
        
        if col_index == -1:
            print(f"No se encontró columna de marca en: {headers}")
            return []

        unique_mvnos = sorted(list(set(row[col_index].strip() for row in values[1:] if len(row) > col_index and row[col_index].strip())))
        #print(f"MVNOs encontrados: {unique_mvnos}")
        return unique_mvnos
        
    except Exception as e:
        print(f"Error al obtener lista de MVNOs: {e}")
        return []

from datetime import datetime

def buscar_portouts(mvno, fecha_desde, fecha_hasta):
    
    sheet = get_connection()
    # Llamada a la api
    try:
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='PORT OUT GUI').execute()
        values = result.get('values', [])
        
        if not values:
            return []

        headers = [str(h).strip().upper() for h in values[0]]
        
        # Mapear índices de columnas
        try:
            col_msisdn = headers.index("MSISDN")
            col_fecha = headers.index("FECHA")
            
            if "MARCA" in headers:
                col_marca = headers.index("MARCA")
            elif "MVNO" in headers:
                col_marca = headers.index("MVNO")
            else:
                 # Fallback si no encuentra la columna exacta
                col_marca = next((i for i, h in enumerate(headers) if "MARCA" in h), -1)

            col_operador = headers.index("OPERADOR")

            if col_marca == -1:
                 print("Columna de MARCA no encontrada")
                 return []

        except ValueError as e:
            print(f"Columna requerida no encontrada: {e}")
            return []

        filtered_data = []
        
        # Convertir fechas de filtro a datetime para comparación
        try:
            desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d') if fecha_desde else None
            hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d') if fecha_hasta else None
        except ValueError:
            print("Error en formato de fechas de filtro")
            return []

        for row in values[1:]: # Saltar header
            # Asegurarse que la fila tenga suficientes columnas
            if len(row) <= max(col_msisdn, col_fecha, col_marca, col_operador):
                continue

            r_marca = row[col_marca].strip()
            r_fecha_str = row[col_fecha].strip()
            
            # Filtro por MVNO
            if mvno and mvno != "Todas" and r_marca != mvno:
                continue
            
            # Filtro por Fecha
            if desde_dt or hasta_dt:
                try:
                    # Asumiendo formato DD/MM/YYYY o YYYY-MM-DD
                    r_fecha_dt = None
                    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d'):
                        try:
                            clean_date = r_fecha_str.split()[0]
                            r_fecha_dt = datetime.strptime(clean_date, fmt)
                            break
                        except ValueError:
                            continue
                    
                    if r_fecha_dt:
                        if desde_dt and r_fecha_dt < desde_dt:
                             continue
                        if hasta_dt and r_fecha_dt > hasta_dt:
                             continue
                    else:
                        continue 

                except Exception as e:
                     print(f"Error procesando fecha fila: {e}")
                     continue

            filtered_data.append({
                "msisdn": row[col_msisdn],
                "fecha": row[col_fecha],
                "marca": r_marca,
                "operador": row[col_operador]
            })

        print(f"Registros filtrados: {len(filtered_data)}")
        return filtered_data

    except Exception as e:
        print(f"Error en buscar_portouts: {e}")
        return []

def generar_excel(data, folder_path):
    if not data:
        return None

    # Crear DataFrame con pandas
    df = pl.DataFrame(data).to_pandas()
    
    # Generar nombre de archivo único
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reporte_portouts_{timestamp}.xlsx"
    filepath = os.path.join(folder_path, filename)

    # Guardar en Excel
    try:
        df.to_excel(filepath, index=False)
        return filename
    except Exception as e:
        print(f"Error generando Excel: {e}")
        return None