from sole_platform import db

class Contracargo(db.Model):
    __tablename__ = "contracargos"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    msisdn = db.Column(db.String(10), nullable=False)
    ord_pay = db.Column(db.String(100))
    email = db.Column(db.String(120), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    paid = db.Column(db.Boolean, default=False)
    descripcion = db.Column(db.Text)
    date_inserted = db.Column(db.DateTime, server_default=db.func.now())
    

    def __init__(self, name, msisdn, ord_pay, email, monto, marca, paid, descripcion, date_inserted=None):
        self.name = name
        self.msisdn = msisdn
        self.ord_pay = ord_pay
        self.email = email
        self.monto = monto
        self.marca = marca
        self.paid = paid
        self.descripcion = descripcion
        if date_inserted:
            self.date_inserted = date_inserted