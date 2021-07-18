from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask("my_app", template_folder='/home/myr/PycharmProjects/ITEA_projrct_CRM/templates')
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@localhost/postgres"
db = SQLAlchemy(app)

"""Модель депрартамента"""


class Departments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    location = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.BigInteger)

    def __str__(self):
        return f"Department {self.name} with id:{self.id} located in {self.location}"

    def __repr__(self):
        res = {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "phone": self.phone
            }
        return str(res)


"""Модель Сотрудника"""


class Employees(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    position = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.BigInteger, nullable=False)
    dep_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)
    chat_id = db.Column(db.BigInteger, unique=True)

    def __str__(self):
        return f"Employee {self.name} with id:{self.id} worked on position {self.position} " \
               f"in department {self.dep_id}, phone number: {self.phone}."

    def __repr__(self):
        res = {
               "id": self.id,
               "name": self.name,
               "position": self.position,
               "phone": self.phone,
               "department_id": self.dep_id
               }
        return str(res)


"""Модель Клиента"""


class Customers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.BigInteger, nullable=False)
    is_problem = db.Column(db.Boolean, default=False)
    is_subscribed = db.Column(db.Boolean, default=False)
    chat_id = db.Column(db.Integer, unique=True)
    username = db.Column(db.String(50), unique=True)

    def __str__(self):
        return f"Customer {self.name}{'!!!'*bool(self.is_problem)} with id:{self.id}, phone number: {self.phone}."

    def __repr__(self):
        res = {
               "id": self.id,
               "name": self.name,
               "phone": self.phone,
               "problem": str(self.is_problem)
               }
        return str(res)


"""Модель Заявки"""


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime)
    status = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    descript = db.Column(db.String(200), nullable=False)
    creator = db.Column(db.Integer, db.ForeignKey("employees.id", ondelete='CASCADE'), nullable=False)
    serial = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, default=0)
    customer = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete='CASCADE'), nullable=False)
    updated = db.Column(db.DateTime)

    def __str__(self):
        return f"Заявка № {self.id} создана {self.created} сотрудником {str(self.creator)}. " \
               f"Актуальный статус: {self.status}, тип: {self.type}, описание: {self.descript}, " \
               f"серийный номер: {self.serial}, последние оновление: {self.updated}. Клиент: {self.customer}."

    def __repr__(self):
        res = {
              "id": self.id,
              "created": self.created.strftime('%d.%m.%Y %H:%M'),
              "status": self.status,
              "type": self.type,
              "description": self.descript,
              "creator": self.creator,
              "serial": self.serial,
              "price": self.price,
              "customer": self.customer
              }
        return str(res)


if __name__ == "__main__":
    db.create_all()
