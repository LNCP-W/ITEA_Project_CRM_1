import pytest
import main
from main import app


@pytest.mark.parametrize('emp_id, ', [(33, ), (5, ), (40, ), (40, )])
def test_employee(emp_id):
    employee = main.Employees.query.filter_by(id=emp_id).first()
    d = [
        f'name="id" value={employee.id}',
        f'name="name" value="{employee.name}"',
        f'name="position" value="{employee.position}"',
        f'name="phone" value="{employee.phone}"',
        f'name="dep_id" value="{employee.dep_id}"'
    ]
    resp = app.test_client().get("/employee", query_string={'id': emp_id})
    html_string = resp.data.decode('utf-8')
    assert resp.status == '200 OK'
    for i in d:
        x = html_string.find(i)
        assert x != -1
