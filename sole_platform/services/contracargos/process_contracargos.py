import polars as pl
from datetime import datetime
import os

def process_contracargos_csv(file_path):
    """
    Lee un archivo CSV con Polars, filtra por contracargos y limpia los datos.
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
        
        # Mapear columnas posibles (para ser flexibles con el CSV de la pasarela)
        # Nombres esperados vs nombres posibles
        col_mappings = {
            "nombre": ["nombre", "name", "cliente"],
            "email": ["email", "correo_electronico", "correo"],
            "telefono": ["telefono", "msisdn", "celular"],
            "monto": ["monto_cargo", "monto"],
            "descripcion": ["descripcion", "description", "detalle"],
            "id_orden": ["id_orden", "ord_pay", "orden", "id"],
            "fecha": ["fecha_creacion", "fecha_pago", "fecha"],
            "tipo_transaccion": ["tipo_transaccion", "transaccion", "tipo"]
        }

        # Renombrar columnas si existen variaciones
        actual_cols = df.columns
        rename_dict = {}
        for target, options in col_mappings.items():
            for opt in options:
                if opt in actual_cols and target not in rename_dict.values():
                    rename_dict[opt] = target
                    break
        
        if rename_dict:
            df = df.rename(rename_dict)

        # Verificar que las columnas mínimas existan
        required_cols = ["nombre", "email", "monto", "id_orden", "fecha", "tipo_transaccion"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Faltan las siguientes columnas o sus equivalentes en el CSV: {', '.join(missing_cols)}")
        
        # Filtrar por tipo_transaccion == 'contracargo' (más flexible con acentos y espacios)
        df_filtered = df.filter(
            pl.col("tipo_transaccion").str.strip_chars()
            .str.to_lowercase()
            .str.replace("ó", "o")
            .str.replace("ó", "o") # Por si es un carácter combinado
            == "contracargo"
        )
        
        # Limpiar y preparar datos
        processed_data = []
        for row in df_filtered.to_dicts():
            
            # Obtener y limpiar MSISDN (teléfono) de estar disponible, si no "S/N"
            msisdn = "S/N"
            if "telefono" in df.columns and row.get("telefono"):
                msisdn = str(row["telefono"]).strip()
                if msisdn.endswith('.0'):
                    msisdn = msisdn[:-2]
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
                    "%Y-%m-%d %H:%M:%S %z",
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
                        return dt # Retornar el datetime completo si se desea, o dt.date()
                    except (ValueError, TypeError):
                        continue
                
                parts = s_date.split(' ')
                if len(parts) > 1:
                    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
                        try:
                            dt = datetime.strptime(parts[0], fmt)
                            return dt
                        except (ValueError, TypeError):
                            continue

                print(f"[DEBUG] No se pudo parsear la fecha '{date_str}' en el campo '{field_name}'")
                return None

            date_inserted = parse_date(row["fecha"], "fecha")
            
            processed_data.append({
                "name": str(row["nombre"]).strip(),
                "email": str(row["email"]).strip(),
                "msisdn": msisdn,
                "monto": float(row["monto"]) if row.get("monto") else 0.0,
                "descripcion": str(row["descripcion"]).strip() if "descripcion" in df.columns and row.get("descripcion") else "",
                "ord_pay": str(row["id_orden"]).strip(),
                "date_inserted": date_inserted,
                "marca": None # Ya que el usuario nos confirmó hacerla nullable
            })
            
        return processed_data
        
    except Exception as e:
        print(f"Error procesando CSV de contracargos: {str(e)}")
        raise e
