from .entities.contracargos import Contracargo
from sole_platform import db

class ModelContracargo:

    @staticmethod
    def get_all_contracargos(page, per_page=5):
        try:
            return Contracargo.query.order_by(Contracargo.date_inserted).paginate(page=page, per_page=per_page)
        except Exception as e:
            raise Exception(f"Error al obtener contracargos: {str(e)}")
    
    @staticmethod
    def add_contracargo(contracargo):
        try:
            db.session.add(contracargo)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error al agregar contracargo: {str(e)}")

    @staticmethod
    def search_contracargos_by_name(name, fecha_desde, fecha_hasta, page, per_page=5):
        
        print(f"fecha_desde: {fecha_desde}, fecha_hasta: {fecha_hasta}")
        
        try:
            search_pattern = f"%{name}%"
            return Contracargo.query.filter(Contracargo.name.ilike(search_pattern)).order_by(Contracargo.date_inserted.desc()).paginate(page=page, per_page=per_page)
        except Exception as e:
            raise Exception(f"Error en la búsqueda: {str(e)}")

    @staticmethod
    def search_contracargos_by_date(fecha_desde, fecha_hasta, page, per_page=5):
        try:
            query = Contracargo.query
            
            if fecha_desde:
                query = query.filter(Contracargo.date_inserted >= fecha_desde)
            if fecha_hasta:
                query = query.filter(Contracargo.date_inserted <= fecha_hasta)
            
            return query.order_by(Contracargo.date_inserted.desc()).paginate(page=page, per_page=per_page)
        except Exception as e:
            raise Exception(f"Error en la búsqueda por fecha: {str(e)}")

    @staticmethod
    def search_contracargos(busqueda, fecha_desde, fecha_hasta, page, per_page=5):
        try:
            query = Contracargo.query

            # 🔹 Filtro por fecha si existe
            if fecha_desde:
                query = query.filter(Contracargo.date_inserted >= fecha_desde)
            if fecha_hasta:
                query = query.filter(Contracargo.date_inserted <= fecha_hasta)

            # 🔹 Detectar tipo de búsqueda
            if busqueda:
                if "@" in busqueda:  # búsqueda por correo
                    query = query.filter(Contracargo.email.ilike(f"%{busqueda}%"))
                elif busqueda.isdigit():  # búsqueda por msisdn
                    query = query.filter(Contracargo.msisdn.ilike(f"%{busqueda}%"))
                elif busqueda.startswith("ord_") or busqueda.startswith("BBVA_"):  # búsqueda por ord_pay
                    query = query.filter(Contracargo.ord_pay.ilike(f"%{busqueda}%"))
                else:  # por defecto: búsqueda por nombre
                    query = query.filter(Contracargo.name.ilike(f"%{busqueda}%"))

            return query.order_by(Contracargo.date_inserted.desc()).paginate(page=page, per_page=per_page)
        
        except Exception as e:
            raise Exception(f"Error en la búsqueda: {str(e)}")

    @staticmethod
    def delete_contracargo(contracargo_id):
        try:
            contracargo = Contracargo.query.get(contracargo_id)
            if contracargo:
                db.session.delete(contracargo)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error al eliminar contracargo: {str(e)}")
        
    @staticmethod
    def edit_contracargo(contracargo_id, ord_pay, paid, descripcion):
        try:
            contracargo = Contracargo.query.get(contracargo_id)
            if contracargo:
                contracargo.ord_pay = ord_pay
                contracargo.paid = paid
                contracargo.descripcion = descripcion
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error al editar contracargo: {str(e)}")
        