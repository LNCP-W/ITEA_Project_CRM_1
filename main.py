import datetime
import flask
from models import app, db, Departments, Employees, Customers, Orders
from flask import request, render_template

if __name__ == "__main__":
    import bot


"""раскомментировать при тестировании"""
# app.config['DEBUG'] = True
# app.config['TESTING'] = True

query_offset = 0


def next_10(req):
    """Увеличение/уменшение смещения отображения результатов на 10 """

    global query_offset
    if 'next' in req.args:
        query_offset += 10
    elif 'prev' in req.args and query_offset > 10:
        query_offset -= 10
    else:
        query_offset = 0
    return query_offset


def if_exist(clas):
    """Проверка на существовние дубликата"""

    exist_emp = clas.query.filter(
        (clas.name == request.values['name']) | (clas.phone == request.values['phone'])).all()
    if exist_emp:
        return render_template('index.html', title="Запись с таким иминем уже существует")


@app.route('/search', methods=["GET"])
def search():
    """Поиск записи по ID
    На вход принимает аргументы: ключ(тип записи) и значение(ID записи)ю
    В зависимости от ключа возвращает: саму запись, привязаныее к нея записи и файл для рендера.
    При отсутствии записи в базе - возвращает главную страницу с оповещением б ошибке"""

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
    res = dict_do[x[0]]
    if not res[0]:
        res = "Нет такого id"
        return render_template('index.html', title='Главная страница', results=res)
    return render_template(res[2], title=res[0].id, results=res)


@app.route('/order', methods=["GET"])
def order():
    """Отображение отдельной заявки. В запросе - id заявки"""

    ord_id = request.args["id"]
    res = Orders.query.filter_by(id=ord_id).first()
    return render_template('order.html', title=ord_id, results=res)


@app.route('/department', methods=["GET"])
def department():
    """Отображение отдельного департамента.
    В запросе - id департамента. Возвращает сам департамент и сотрудников которые к нему привязаны"""

    dep_id = request.args["id"]
    res = [Departments.query.filter_by(id=dep_id).first(), Employees.query.filter_by(dep_id=dep_id).limit(10).all()]
    return render_template('department.html', title=dep_id, results=res)


@app.route('/customer', methods=["GET"])
def customer():
    """Отображение отдельного клиента.
    В запросе - id клиента. Возвращает самого клиента и заявки которые к нему привязаны.
    Если в запросе присутствует ключ status или date отображаюся только данные отфильтрованы по значению ключя.
    """
    query_offset = next_10(request)  # увеличение query.offset по запросу
    customer_id = request.args["id"]
    customer = Customers.query.filter_by(id=customer_id).first()
    if "status" in request.args:
        orders = Orders.query.filter_by(
                customer=customer_id,
                status=request.args["status"]
            ).limit(10).offset(query_offset).all()
    elif "date" in request.args:
        date = datetime.datetime.strptime(request.args["date"], "%Y-%m-%d")
        orders = Orders.query.filter_by(customer=customer_id).filter(
            Orders.created >= date
            ).filter(Orders.created < date + datetime.timedelta(days=1)).limit(10).offset(query_offset).all()
    else:
        orders = Orders.query.filter_by(customer=customer_id).limit(10).offset(query_offset).all()
    res = [customer, orders]
    return render_template('customer.html', title=customer_id, results=res)


@app.route('/employee', methods=["GET"])
def employee():
    """Отображение отдельного работника.
    В запросе - id работника. Возвращает самого работника и заявки которые к нему привязаны.
    Если в запросе присутствует ключ status или date отображаюся только данные отфильтрованы по значению ключя.
    """

    query_offset = next_10(request)  # увеличение query.offset по запросу
    emp_id = request.args["id"]
    if "status" in request.args:
        ordrs = Orders.query.filter_by(
            creator=emp_id,
            status=request.args["status"]
        ).limit(10).offset(query_offset).all()
    elif "date" in request.args:
        date = datetime.datetime.strptime(request.args["date"], "%Y-%m-%d")
        ordrs = Orders.query.filter_by(creator=emp_id).filter(
            Orders.created >= date
        ).filter(Orders.created < date + datetime.timedelta(days=1)).limit(10).offset(query_offset).all()
    else:
        ordrs = Orders.query.filter_by(creator=emp_id).limit(10).offset(query_offset).all()
    employee = Employees.query.filter_by(id=emp_id).first()
    res = (employee, ordrs)
    if not res[0]:
        emp_id = "Нет такого id"
    return render_template('employee.html', title=emp_id, results=res)


@app.route('/all_customers')
def all_customers():
    """Отображение всех клиентов.(порционно по 10 шт) """

    query_offset = next_10(request)  # увеличение query.offset по запросу
    data = Customers.query.limit(10).offset(query_offset).all()
    return render_template('customers.html', title="Клиенты", results=data)


@app.route('/all_orders')
def all_orders():
    """Отображение всех Заявок.(порционно по 10 шт)
    Если в запросе есть ключь status или date - идет фильтрация по значению ключя"""

    query_offset = next_10(request)  # увеличение query.offset по запросу
    if "status" in request.args:
        if request.args["status"] == 'activ':  # Отображение всех активных заявок
            orders = Orders.query.filter(
                (Orders.status == "Новый") |
                (Orders.status == "В работе") |
                (Orders.status == "Ждет запчасть")
                ).limit(10).offset(query_offset).all()
        else:
            orders = Orders.query.filter_by(status=request.args["status"]).limit(10).all()
    elif "date" in request.args:
        date = datetime.datetime.strptime(request.args["date"], "%Y-%m-%d")
        orders = Orders.query.filter(Orders.created >= date).filter(
            Orders.created < date + datetime.timedelta(days=1)
            ).limit(10).offset(query_offset).all()
    else:
        orders = Orders.query.limit(10).offset(query_offset).all()
    return render_template('orders.html', title="Заявки", results=orders)


@app.route('/all_employees')
def all_employees():
    """Отображение всех сотрудников.(порционно по 10 шт) """

    query_offset = next_10(request)  # увеличение query.offset по запросу
    data = Employees.query.limit(10).offset(query_offset).all()
    return render_template('employees.html', title='Сотрудники', results=data)


@app.route('/all_departments')
def all_departments():
    """Отображение всех департаментов.(порционно по 10 шт) """

    query_offset = next_10(request)  # увеличение query.offset по запросу
    data = Departments.query.limit(10).offset(query_offset).all()
    return render_template('departments.html', title='Департаменты', results=data)


@app.route('/edit_department', methods=["POST"])
def edit_department():
    """Изминение данных депртамента """

    dep_id = request.values['id']
    dep = Departments.query.filter_by(id=dep_id).first()
    dep.name = request.values["name"]
    dep.location = request.values["location"]
    dep.phone = request.values["phone"]
    db.session.commit()
    return flask.redirect(f"/department?id={dep_id}")


@app.route('/edit_employee', methods=["POST"])
def edit_employee():
    """Изминение данных работника """

    emp = Employees.query.filter_by(id=request.values["id"]).first()
    emp.name = request.values["name"]
    emp.position = request.values["position"]
    emp.phone = request.values["phone"]
    emp.dep_id = request.values["dep_id"]
    db.session.commit()
    return flask.redirect(f"/employee?id={emp.id}")


@app.route('/edit_customer', methods=["POST"])
def edit_customer():
    """Изминение данных клиента """

    customer = Customers.query.filter_by(id=request.values["id"]).first()
    customer.name = request.values["name"]
    customer.phone = request.values["phone"]
    if 'is_problem' in request.values:
        customer.is_problem = bool(request.values['is_problem'])
    else:
        customer.is_problem = 0
    db.session.commit()
    return flask.redirect(f"/customer?id={customer.id}")


@app.route('/edit_order', methods=["POST"])
def edit_order():
    """Изминение данных заявки.
    Оновляется время обновления заявки.
    При изминении статуса - отправка сообщения клиенту в телеграмбот(если подписан) """

    ord = Orders.query.filter_by(id=request.values["id"]).first()
    old_status = ord.status
    ord.creator = request.values["creator"]
    ord.status = request.values["status"]
    ord.type = request.values["type"]
    ord.descript = request.values["descript"]
    ord.serial = request.values["serial"]
    ord.price = request.values["price"]
    ord.updated = datetime.datetime.now()
    db.session.commit()
    if old_status != request.values["status"]:
        cust_chat_id = Customers.query.filter_by(id=ord.customer).first().chat_id
        if cust_chat_id:
            bot.send_notification(cust_chat_id, f"Статус заяви №{ord.id} изменен: {request.values['status']}")
    return flask.redirect(f"/order?id={ord.id}")


@app.route("/create_dep", methods=["POST"])
def create_dep():
    """Создание департамента(страница создания и метод создания)
    если нет аргументов - отображет страницу.
    Если существует депратамент с вводимым именем или телефоном - выдает ошибку"""

    if not request.values:
        return render_template('create_dep.html', title='Cоздание департамента')
    else:
        if if_exist(Departments):  # Проверка на дубли
            return if_exist(Departments)
        new_dep = Departments(**request.values)
        db.session.add(new_dep)
        db.session.commit()
        return flask.redirect(f"/department?id={new_dep.id}")


@app.route("/create_customer", methods=["POST"])
def create_customer():
    """Создание клиента (страница создания и метод создания)
    если нет аргументов - отображет страницу.
    Если существует клиент с вводимым именем или телефоном  - выдает ошибку"""

    if not request.values:
        return render_template('create_customer.html', title='Регистрация Клиента ')
    else:
        if if_exist(Customers):  # Проверка на дубли
            return if_exist(Customers)
        new_cust = Customers(**request.values)
        db.session.add(new_cust)
        db.session.commit()
        return flask.redirect(f"/customer?id={new_cust.id}")


@app.route("/create_emp", methods=["POST"])
def create_emp():
    """Создание Работника (страница создания и метод создания)
    если нет аргументов - отображет страницу.
    Если существует работник с вводимым именем или телефоном  - выдает ошибку"""

    if len(request.values) < 2:
        return render_template('create_emp.html', title='Регистрация Сотрудника', id=request.values['id'])
    else:
        if if_exist(Customers):  # Проверка на дубли
            return if_exist(Customers)
        new_emp = Employees(**request.values)
        db.session.add(new_emp)
        db.session.commit()
        return flask.redirect(f"/employee?id={new_emp.id}")


@app.route("/create_ord", methods=["POST"])
def create_ord():
    """Создание заявки (страница создания и метод создания)
    если нет аргументов - отображет страницу.
    Автоматически добавляется дата создания/оновления.
    Если сотрудник/работник подписаны - отправка сообщения о создании заявки"""

    if len(request.values) < 2:
        page_title = 'Регистрация Заявки'
        customers = Customers.query.all()
        return render_template(
            'create_order.html',
            title=page_title,
            creator=request.values['creator'],
            customers=customers)
    else:
        date = {'created': datetime.datetime.now(), 'updated': datetime.datetime.now()}
        date.update(**request.values)
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


@app.route("/delete_dep", methods=["POST"])
def delete_dep():
    """Удаление департамента (удалятся все привязаные сотрудники и их заявки)"""

    dep = Departments.query.filter_by(id=request.values['id']).first()
    db.session.delete(dep)
    db.session.commit()
    return flask.redirect("/all_departments")


@app.route("/delete_emp", methods=["POST"])
def delete_emp():
    """Удаление сотрудника (удалятся все привязаные заявки)"""

    dep = Employees.query.filter_by(id=request.values['id']).first()
    db.session.delete(dep)
    db.session.commit()
    return flask.redirect("/all_employees")


@app.route("/delete_cust", methods=["POST"])
def delete_cust():
    """Удаление клиента (удалятся все привязаные заявки)"""

    dep = Customers.query.filter_by(id=request.args['id']).first()
    db.session.delete(dep)
    db.session.commit()
    return flask.redirect("/all_customers")


@app.route("/delete_ordr", methods=["POST"])
def delete_ordr():
    """Удаление заявки"""

    ordr = Orders.query.filter_by(id=request.values['id']).first()
    if not ordr:
        return all_orders()
    db.session.delete(ordr)
    db.session.commit()
    return flask.redirect("/all_orders")


@app.route("/send_to_cust", methods=["POST"])
def send_to_cust():
    """Отправка сообщения клиенту"""

    chat_id = Customers.query.filter_by(id=request.values['id']).first().chat_id
    bot.send_notification(chat_id, request.values['text'])
    return flask.redirect(f"/customer?id={request.values['id']}")


@app.route("/notificate_employees", methods=["GET"])
def notificate_employees():
    """Отправка сообщения всем сотрудникам(если подписан) со списком открытых заявон на каждого"""

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


@app.route("/")
@app.route("/index")
def index():
    """Главная страница"""

    return render_template('index.html', title='Главная страница')


@app.route("/help")
def help_docum():
    """Страница с инструкциями"""

    return render_template('help.html', title="Помощь")


if __name__ == "__main__":
    app.run()
