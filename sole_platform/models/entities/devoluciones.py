from sole_platform import db

class Devolucion(db.Model):
    __tablename__ = "devoluciones"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    msisdn = db.Column(db.String(12), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.Text)
    ord_pay = db.Column(db.String(100))
    date_pay = db.Column(db.Date)
    date_return = db.Column(db.Date)
    

    def __init__(self, name, msisdn, email, monto, descripcion, ord_pay, date_pay, date_return):
        self.name = name
        self.msisdn = msisdn
        self.email = email
        self.monto = monto
        self.descripcion = descripcion
        self.ord_pay = ord_pay
        self.date_pay = date_pay
        self.date_return = date_return
