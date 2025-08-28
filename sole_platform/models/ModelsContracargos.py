from .entities.contracargos import Contracargo
from sole_platform import db

class ModelContracargo:

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
    def get_all_contracargos(page, per_page=10):
        try:
            return Contracargo.query.order_by(Contracargo.date_inserted.desc()).paginate(page=page, per_page=per_page)
        except Exception as e:
            raise Exception(f"Error al obtener contracargos: {str(e)}")

    @staticmethod
    def search_contracargos_by_name(name, page, per_page=10):
        try:
            search_pattern = f"%{name}%"
            return Contracargo.query.filter(Contracargo.name.ilike(search_pattern)).order_by(Contracargo.date_inserted.desc()).paginate(page=page, per_page=per_page)
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
    def edit_contracargo(contracargo_id, name, email):
        try:
            contracargo = Contracargo.query.get(contracargo_id)
            if contracargo:
                contracargo.name = name
                contracargo.email = email
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error al editar contracargo: {str(e)}")
        