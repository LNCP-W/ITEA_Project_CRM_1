import pytest
import main
from main import app


@pytest.mark.parametrize('dep_id, ', [(1, ), (87, ), (88, ), (89, )])
def test_department(dep_id):
    department = main.Departments.query.filter_by(id=dep_id).first()
    d = [
        f'name="id" value={department.id}',
        f'name="name" value="{department.name}"',
        f'name="location" value="{department.location}"',
        f'name="phone" value="{department.phone}"'
    ]
    resp = app.test_client().get("/department", query_string={'id': dep_id})
    html_string = resp.data.decode('utf-8')
    assert resp.status == '200 OK'
    for i in d:
        x = html_string.find(i)
        assert x != -1
