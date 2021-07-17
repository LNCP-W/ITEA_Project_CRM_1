import pytest
import main
from main import create_dep, app, db
@pytest.mark.parametrize('data_in, data_out', [
        (
            {'name': 'first', 'location': 'second', 'phone': 3},
            'first, second, 3'
        ),
        (
            {'name': 'six', 'location': 'seven', 'phone': 8},
            'six, seven, 8'
        )
    ])
def test_create_dep(data_in, data_out):
    resp = app.test_client().get("/create_dep", query_string=data_in)
    assert resp.status == '302 FOUND'
    res = main.Departments.query.filter_by(name=data_in['name']).first()
    assert res.name == data_in['name']
    assert res.location == data_in['location']
    assert res.phone == data_in['phone']
    result = f"{res.name}, {res.location}, {res.phone}"
    assert result == data_out
    db.session.delete(res)
    db.session.commit()





