import polars as pl
from datetime import datetime
import os

def process_returns_csv(file_path):
    """
    Lee un archivo CSV con Polars, filtra por devoluciones y limpia los datos.
    """
    try:
        # Intentar leer el CSV (manejando posibles separadores y codificaciones)
        try:
            df = pl.read_csv(file_path, ignore_errors=True)
            # Verificar si se leyó correctamente (más de una columna)
            if len(df.columns) <= 1:
                df = pl.read_csv(file_path, separator=";", ignore_errors=True)
        except Exception:
            df = pl.read_csv(file_path, separator=";", ignore_errors=True)
        
        # Columnas requeridas
        required_cols = [
            "nombre", "email", "telefono", "monto_cargo", 
            "descripcion", "id_orden", "fecha_pago", 
            "fecha_devolucion", "tipo_transaccion"
        ]
        
        # Verificar que las columnas existan
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Faltan las siguientes columnas en el CSV: {', '.join(missing_cols)}")
        
        # Filtrar por tipo_transaccion == 'devolucion' (más flexible con acentos y espacios)
        df_filtered = df.filter(
            pl.col("tipo_transaccion").str.strip_chars()
            .str.to_lowercase()
            .str.replace("ó", "o")
            .str.replace("ó", "o") # Por si es un carácter combinado
            == "devolucion"
        )
        
        # Limpiar y preparar datos
        processed_data = []
        for row in df_filtered.to_dicts():
            # Limpiar teléfono (msisdn) a 10 dígitos
            msisdn = str(row["telefono"]).strip()
            # Quitar posibles decimales si vienen de Excel (.0)
            if msisdn.endswith('.0'):
                msisdn = msisdn[:-2]
                
            # Si tiene más de 10 dígitos, tomamos los últimos 10
            if len(msisdn) > 10:
                msisdn = msisdn[-10:]
            
            # Parsear fechas
            def parse_date(date_str, field_name):
                if not date_str or str(date_str).strip().lower() in ("null", "nan", "", "none"):
                    return None
                
                s_date = str(date_str).strip()
                if s_date.endswith('.0'):
                    s_date = s_date[:-2]
                
                formats = (
                    "%Y-%m-%d %H:%M:%S %z", # Formato con zona horaria (ej: 2026-03-09 02:47:57 -0600)
                    "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", 
                    "%d/%m/%Y %H:%M:%S %z", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y",
                    "%m/%d/%Y %H:%M:%S %z", "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M", "%m/%d/%Y",
                    "%Y/%m/%d %H:%M:%S %z", "%Y/%m/%d %H:%M:%S", "%Y/%m/%d %H:%M", "%Y/%m/%d",
                    "%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M", "%d-%m-%Y",
                    "%m-%d-%Y %H:%M:%S", "%m-%d-%Y %H:%M", "%m-%d-%Y"
                )
                
                for fmt in formats:
                    try:
                        dt = datetime.strptime(s_date, fmt)
                        return dt.date() # Retornar solo la fecha para coincidir con el tipo DATE de MySQL
                    except (ValueError, TypeError):
                        continue
                
                # Fallback: intentar tomar solo el primer componente (fecha sin hora/zona)
                parts = s_date.split(' ')
                if len(parts) > 1:
                    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
                        try:
                            dt = datetime.strptime(parts[0], fmt)
                            return dt.date()
                        except (ValueError, TypeError):
                            continue

                print(f"[DEBUG] No se pudo parsear la fecha '{date_str}' en el campo '{field_name}'")
                return None

            date_pay = parse_date(row["fecha_pago"], "fecha_pago")
            date_return = parse_date(row["fecha_devolucion"], "fecha_devolucion")
            
            processed_data.append({
                "name": str(row["nombre"]).strip(),
                "email": str(row["email"]).strip(),
                "msisdn": msisdn,
                "monto": float(row["monto_cargo"]),
                "descripcion": str(row["descripcion"]).strip() if row["descripcion"] else "",
                "ord_pay": str(row["id_orden"]).strip(),
                "date_pay": date_pay,
                "date_return": date_return
            })
            
        return processed_data
        
    except Exception as e:
        print(f"Error procesando CSV de devoluciones: {str(e)}")
        raise e
