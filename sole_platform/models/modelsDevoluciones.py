from .entities.devoluciones import Devolucion
from sole_platform import db

class ModelDevolucion:

    @staticmethod
    def get_all_devoluciones(page, per_page=5):
        try:
            return Devolucion.query.order_by(Devolucion.date_pay).paginate(page=page, per_page=per_page)
        except Exception as e:
            raise Exception(f"Error al obtener devoluciones: {str(e)}")
    
    @staticmethod
    def add_devolucion(devolucion):
        try:
            db.session.add(devolucion)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error al agregar devolucion: {str(e)}")

    @staticmethod
    def search_devoluciones_by_name(name, fecha_desde, fecha_hasta, page, per_page=5):
        
        print(f"fecha_desde: {fecha_desde}, fecha_hasta: {fecha_hasta}")
        
        try:
            search_pattern = f"%{name}%"
            return Devolucion.query.filter(Devolucion.name.ilike(search_pattern)).order_by(Devolucion.date_pay.desc()).paginate(page=page, per_page=per_page)
        except Exception as e:
            raise Exception(f"Error en la búsqueda: {str(e)}")

    @staticmethod
    def search_devoluciones_by_date(fecha_desde, fecha_hasta, page, per_page=5):
        try:
            query = Devolucion.query
            
            if fecha_desde:
                query = query.filter(Devolucion.date_pay >= fecha_desde)
            if fecha_hasta:
                query = query.filter(Devolucion.date_pay <= fecha_hasta)
            
            return query.order_by(Devolucion.date_pay.desc()).paginate(page=page, per_page=per_page)
        except Exception as e:
            raise Exception(f"Error en la búsqueda por fecha: {str(e)}")

    @staticmethod
    def search_devoluciones(busqueda, fecha_desde, fecha_hasta, page, per_page=5):
        try:
            query = Devolucion.query

            # 🔹 Filtro por fecha si existe
            if fecha_desde:
                query = query.filter(Devolucion.date_pay >= fecha_desde)
            if fecha_hasta:
                query = query.filter(Devolucion.date_pay <= fecha_hasta)

            # 🔹 Detectar tipo de búsqueda
            if busqueda:
                if "@" in busqueda:  # búsqueda por correo
                    query = query.filter(Devolucion.email.ilike(f"%{busqueda}%"))
                elif busqueda.isdigit():  # búsqueda por msisdn
                    query = query.filter(Devolucion.msisdn.ilike(f"%{busqueda}%"))
                elif busqueda.startswith("ord_") or busqueda.startswith("BBVA_"):  # búsqueda por ord_pay
                    query = query.filter(Devolucion.ord_pay.ilike(f"%{busqueda}%"))
                else:  # por defecto: búsqueda por nombre
                    query = query.filter(Devolucion.name.ilike(f"%{busqueda}%"))

            return query.order_by(Devolucion.date_pay.desc()).paginate(page=page, per_page=per_page)
        
        except Exception as e:
            raise Exception(f"Error en la búsqueda: {str(e)}")

    @staticmethod
    def delete_devolucion(devolucion_id):
        try:
            devolucion = Devolucion.query.get(devolucion_id)
            if devolucion:
                db.session.delete(devolucion)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error al eliminar devolucion: {str(e)}")
        
    @staticmethod
    def edit_devolucion(devolucion_id, ord_pay, paid, descripcion):
        try:
            devolucion = Devolucion.query.get(devolucion_id)
            if devolucion:
                devolucion.ord_pay = ord_pay
                devolucion.paid = paid
                devolucion.descripcion = descripcion
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error al editar devolucion: {str(e)}")

    @staticmethod
    def add_devoluciones_batch(devoluciones_data):
        """
        Agrega múltiples devoluciones a la base de datos, evitando duplicados por ord_pay.
        Retorna (agregados, duplicados, errores)
        """
        agregados = 0
        duplicados = 0
        errores = 0
        
        try:
            # Obtener todos los ord_pay existentes para verificación rápida
            existing_ord_pays = {d.ord_pay for d in Devolucion.query.all() if d.ord_pay}
            
            for item in devoluciones_data:
                ord_pay = item.get("ord_pay")
                
                if ord_pay in existing_ord_pays:
                    duplicados += 1
                    continue
                
                try:
                    nueva = Devolucion(
                        name=item["name"],
                        msisdn=item["msisdn"],
                        email=item["email"],
                        monto=item["monto"],
                        descripcion=item["descripcion"],
                        ord_pay=item["ord_pay"],
                        date_pay=item["date_pay"],
                        date_return=item["date_return"]
                    )
                    db.session.add(nueva)
                    agregados += 1
                    # Añadir al set de existentes para evitar duplicados dentro del mismo batch
                    existing_ord_pays.add(ord_pay)
                except Exception as ex:
                    print(f"Error al procesar fila {item}: {ex}")
                    errores += 1
            
            db.session.commit()
            return agregados, duplicados, errores
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error en inserción masiva: {str(e)}")