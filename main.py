import datetime
import json

from models import app, db, Departments, Employees, Customers, Orders
from flask import Flask, request, render_template

@app.route('/search', methods=["GET"])
def search():
    for x in request.args.items():
        dict_do = {
            'Заявки': [Orders.query.filter_by(id=x[1]).first(), 1, 'order.html'],
            'Сотрудники': [
                        Employees.query.filter_by(id=x[1]).first(),
                        Orders.query.filter_by(creator=x[1]).limit(10).all(),
                        'employee.html'
                        ],
            'Департаменты': [
                        Departments.query.filter_by(id=x[1]).first(),
                        Employees.query.filter_by(dep_id=x[1]).limit(10).all(),
                        'department.html'
                        ],
            'Клиенты': [
                        Customers.query.filter_by(id=x[1]).first(),
                        Orders.query.filter_by(customer=x[1]).limit(10).all(),
                        'customer.html'
                        ]
            }
    res=dict_do[x[0]]

    if not res[0]:
        res= "Нет такого id"
        return render_template('index.html', title='Главная страница', results=res)
    return render_template(res[2], title=res[0].id, results=res)


@app.route('/all_customers')
def all_customers():
    data = Customers.query.limit(10).all()
    page_title = "Клиенты"
    return render_template('customers.html', title=page_title, results=data)

@app.route('/all_orders')
def all_orders():
    data = Orders.query.limit(10).all()
    page_title = "Заявки"
    return render_template('orders.html', title=page_title, results=data)


@app.route('/all_employees')
def all_employees():
    data = Employees.query.limit(10).all()
    page_title = 'Сотрудники'
    return render_template('employees.html', title=page_title, results=data)


@app.route('/all_departments')
def all_departments():
    data = Departments.query.limit(10).all()
    page_title = 'Департаменты'
    return render_template('departments.html', title=page_title, results=data)

@app.route('/edit_department', methods=["GET"])
def edit_department():
    dep = Departments.query.filter_by(id=request.args["id"]).first()
    dep.name = request.args["name"]
    dep.location = request.args["location"]
    dep.phone = request.args["phone"]
    db.session.commit()
    request.args={"Департаменты":request.args["id"]}
    return search()

@app.route('/edit_employee', methods=["GET"])
def edit_employee():
    emp = Employees.query.filter_by(id=request.args["id"]).first()
    emp.name = request.args["name"]
    emp.position = request.args["position"]
    emp.phone = request.args["phone"]
    emp.dep_id = request.args["dep_id"]
    db.session.commit()
    request.args={"Сотрудники": request.args["id"]}
    return search()

@app.route('/edit_order', methods=["GET"])
def edit_order():
    ord = Orders.query.filter_by(id=request.args["id"]).first()
    ord.creator = request.args["creator"]
    ord.status = request.args["status"]
    ord.type = request.args["type"]
    ord.descript = request.args["descript"]
    ord.serial = request.args["serial"]
    ord.price = request.args["price"]
    ord.updated = datetime.datetime.now()
    db.session.commit()
    request.args={"Заявки": request.args["id"]}
    return search()

@app.route("/create_dep")
def create_dep():
    if not request.args:
        page_title = 'Cоздание департамента'
        return render_template('create_dep.html', title=page_title)
    else:
        new_dep = Departments(**request.args)
        db.session.add(new_dep)
        db.session.commit()
        request.args = {"Департаменты": new_dep.id}
        return search()


@app.route("/create_customer")
def create_customer():
    if not request.args:
        page_title = 'Регистрация Клиента '
        return render_template('create_customer.html', title=page_title)
    else:
        new_cli = Customers(**request.args)
        db.session.add(new_cli)
        db.session.commit()
        request.args = {"Клиенты": new_cli.id}
        return search()

@app.route("/create_emp")
def create_emp():
    if len(request.args) < 2:
        page_title = 'Регистрация Сотрудника '
        return render_template('create_emp.html', title=page_title, id=request.args['id'])
    else:
        new_emp = Employees(**request.args)
        db.session.add(new_emp)
        db.session.commit()
        request.args = {"Сотрудники": new_emp.id}
        return search()

@app.route("/create_ord")
def create_ord():
    if len(request.args) < 2:
        page_title = 'Регистрация Заявки'
        customers = Customers.query.all()
        return render_template('create_order.html', title=page_title, creator=request.args['creator'], customers=customers)
    else:
        date={'created':datetime.datetime.now(), 'updated':datetime.datetime.now()}
        date.update(**request.args)
        new_ord = Orders(**date)
        db.session.add(new_ord)
        db.session.commit()
        request.args = {"Заявки": new_ord.id}
        return search()

@app.route("/delete_dep")
def delete_dep():
    dep = Departments.query.filter_by(id=request.args['id']).first()
    db.session.delete(dep)
    db.session.commit()
    return all_departments()


@app.route("/delete_emp")
def delete_emp():
    dep = Employees.query.filter_by(id=request.args['id']).first()
    db.session.delete(dep)
    db.session.commit()
    return all_employees()

@app.route("/index")
def index():
    page_title = 'Главная страница'
    return render_template('index.html', title=page_title)

app.run()


