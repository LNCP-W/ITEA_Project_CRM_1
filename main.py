import datetime
import json

import flask

if __name__ == "__main__":
    import bot


from models import app, db, Departments, Employees, Customers, Orders
from flask import Flask, request, render_template
app.config['DEBUG'] = True
app.config['TESTING'] = True

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


@app.route('/order', methods=["GET"])
def order():
    id = request.args["id"]
    res = Orders.query.filter_by(id=id).first()
    return render_template('order.html', title=id, results=res)

@app.route('/department', methods=["GET"])
def department():
    id = request.args["id"]
    res = [Departments.query.filter_by(id=id).first(), Employees.query.filter_by(dep_id=id).limit(10).all()]
    return render_template('department.html', title=id, results=res)

@app.route('/customer', methods=["GET"])
def customer():
    id = request.args["id"]
    if "status" in request.args:
        ordrs = Orders.query.filter_by(customer=id, status=request.args["status"]).limit(10).all()
    elif "date" in request.args:
        date = datetime.datetime.strptime(request.args["date"], "%Y-%m-%d")
        ordrs = Orders.query.filter_by(customer=id).filter(
            Orders.created>=date
            ).filter(Orders.created < date + datetime.timedelta(days=1)).limit(10).all()
    else:
        ordrs = Orders.query.filter_by(customer=id).limit(10).all()
    res = [Customers.query.filter_by(id=id).first(), ordrs]
    return render_template('customer.html', title=id, results=res)

@app.route('/employee', methods=["GET"])
def employee():
    id = request.args["id"]
    if "status" in request.args:
        ordrs = Orders.query.filter_by(creator=id, status=request.args["status"]).limit(10).all()
    elif "date" in request.args:
        date = datetime.datetime.strptime(request.args["date"], "%Y-%m-%d")
        ordrs = Orders.query.filter_by(creator=id).filter(
            Orders.created>=date
            ).filter(Orders.created < date + datetime.timedelta(days=1)).limit(10).all()
    else:
        ordrs = Orders.query.filter_by(creator=id).limit(10).all()
    res = (Employees.query.filter_by(id=id).first(),
    ordrs)
    if not res[0]: id = "Нет такого id"
    return render_template('employee.html', title=id, results=res)

@app.route('/all_customers')
def all_customers():
    data = Customers.query.limit(10).all()
    page_title = "Клиенты"
    return render_template('customers.html', title=page_title, results=data)

@app.route('/all_orders')
def all_orders():
    if "status" in request.args:
        if request.args["status"] == 'activ':
            ordrs = Orders.query.filter(
                (Orders.status == "Новый") |
                (Orders.status == "В работе") |
                (Orders.status == "Ждет запчасть")
                ).limit(10).all()
        else:
            ordrs = Orders.query.filter_by(status=request.args["status"]).limit(10).all()
    elif "date" in request.args:
        date = datetime.datetime.strptime(request.args["date"], "%Y-%m-%d")
        ordrs = Orders.query.filter(Orders.created>=date).filter(
            Orders.created < date + datetime.timedelta(days=1)
            ).limit(10).all()
    else:
        ordrs = Orders.query.limit(10).all()
    page_title = "Заявки"
    return render_template('orders.html', title=page_title, results=ordrs)


@app.route('/all_employees')
def all_employees():
    data = Employees.query.limit(10).all()
    page_title = 'Сотрудники'
    return render_template('employees.html', title=page_title, results=data)

x = 0

@app.route('/all_departments')
def all_departments():
    nn=request
    global x
    if 'sas' in request.args:
        x += 10
    else:
        x = 0
    data = Departments.query[x:x+10]
    page_title = 'Департаменты'
    return render_template('departments.html', title=page_title, results=data)

@app.route('/edit_department', methods=["GET"])
def edit_department():
    id = request.args['id']
    dep = Departments.query.filter_by(id=id).first()
    dep.name = request.args["name"]
    dep.location = request.args["location"]
    dep.phone = request.args["phone"]
    db.session.commit()
    return flask.redirect(f"/department?id={id}")

@app.route('/edit_employee', methods=["POST"])
def edit_employee():
    emp = Employees.query.filter_by(id=request.values ["id"]).first()
    emp.name = request.values["name"]
    emp.position = request.values["position"]
    emp.phone = request.values["phone"]
    emp.dep_id = request.values["dep_id"]
    db.session.commit()
    request.args={"id": request.values["id"]}
    return flask.redirect(f"/employee?id={emp.id}")


@app.route('/edit_customer', methods=["POST"])
def edit_customer():
    cust = Customers.query.filter_by(id=request.values ["id"]).first()
    cust.name = request.values["name"]
    cust.phone = request.values["phone"]
    if 'is_problem' in request.values:
        cust.is_problem = bool(request.values['is_problem'])
    else:cust.is_problem = 0
    db.session.commit()
    request.args={"id": request.values["id"]}
    return flask.redirect(f"/customer?id={cust.id}")

@app.route('/edit_order', methods=["GET"])
def edit_order():
    ord = Orders.query.filter_by(id=request.args["id"]).first()
    old_status = ord.status
    ord.creator = request.args["creator"]
    ord.status = request.args["status"]
    ord.type = request.args["type"]
    ord.descript = request.args["descript"]
    ord.serial = request.args["serial"]
    ord.price = request.args["price"]
    ord.updated = datetime.datetime.now()
    db.session.commit()
    if old_status != request.args["status"]:
        customer = Customers.query.filter_by(id=ord.customer).first().chat_id
        if customer:
            bot.send_notification(customer, f"Статус заяви №{ord.id} изменен: {request.args['status']}")
    return flask.redirect(f"/order?id={ord.id}")

@app.route("/create_dep")
def create_dep():
    if not request.args:
        page_title = 'Cоздание департамента'
        return render_template('create_dep.html', title=page_title)
    else:
        new_dep = Departments(**request.args)
        db.session.add(new_dep)
        db.session.commit()
        return flask.redirect(f"/department?id={new_dep.id}")


@app.route("/create_customer")
def create_customer():
    if not request.args:
        page_title = 'Регистрация Клиента '
        return render_template('create_customer.html', title=page_title)
    else:
        new_cli = Customers(**request.args)
        db.session.add(new_cli)
        db.session.commit()
        return flask.redirect(f"/customer?id={new_cli.id}")

@app.route("/create_emp")
def create_emp():
    if len(request.args) < 2:
        page_title = 'Регистрация Сотрудника '
        return render_template('create_emp.html', title=page_title, id=request.args['id'])
    else:
        new_emp = Employees(**request.args)
        db.session.add(new_emp)
        db.session.commit()
        return flask.redirect(f"/employee?id={new_emp.id}")

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
        customer_chat_id = Customers.query.filter_by(id=new_ord.customer).first().chat_id
        employee_chat_id = Employees.query.filter_by(id=new_ord.creator).first().chat_id
        if customer_chat_id:
            bot.send_notification(customer_chat_id, f"Создана заявка: {new_ord}")
        if employee_chat_id:
            bot.send_notification(employee_chat_id, f"Создана заявка: {new_ord}")
        return flask.redirect(f"/order?id={new_ord.id}")

@app.route("/delete_dep")
def delete_dep():
    dep = Departments.query.filter_by(id=request.args['id']).first()
    db.session.delete(dep)
    db.session.commit()
    return flask.redirect("/all_departments")

@app.route("/notificate_employees")
def notificate_employees():
    for employee in Employees.query.all():
        orders = Orders.query.filter_by(creator=employee.id).filter(
            (Orders.status == "Новый") |
            (Orders.status == "В работе") |
            (Orders.status == "Ждет запчасть")
        ).all()
        if employee.chat_id:
            bot.send_notification(employee.chat_id, f"У вас {len(orders)} заявок:")
            for order in orders:
                bot.send_notification(employee.chat_id, order)
    return flask.redirect("/all_employees")


@app.route("/delete_emp")
def delete_emp():
    dep = Employees.query.filter_by(id=request.args['id']).first()
    db.session.delete(dep)
    db.session.commit()
    return flask.redirect("/all_employees")

@app.route("/delete_cust")
def delete_cust():
    dep = Customers.query.filter_by(id=request.args['id']).first()
    if not dep: return all_customers()
    db.session.delete(dep)
    db.session.commit()
    return flask.redirect("/all_customers")


@app.route("/delete_ordr")
def delete_ordr():
    ordr = Orders.query.filter_by(id=request.values['id']).first()
    if not ordr: return all_orders()
    db.session.delete(ordr)
    db.session.commit()
    return flask.redirect("/all_orders")

@app.route("/send_to_cust")
def send_to_cust():
    chat_id = Customers.query.filter_by(id=request.args['id']).first().chat_id
    bot.send_notification(chat_id, request.args['text'])
    return flask.redirect(f"/customer?id={request.args['id']}")


@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html', title='Главная страница')

@app.route("/help")
def help():
    return render_template('help.html', title="Помощь")

if __name__ == "__main__":
    app.run()


