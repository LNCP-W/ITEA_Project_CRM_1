import pytest
import main
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
    # data_in = {'name': 'first', 'location': 'second', 'phone': 3 }
    # data_out = 'first, second, 3'
    test_client = app.test_client()
    resp = app.test_client().get("/create_dep", query_string=data_in)
    assert resp.status == '200 OK'
    res = main.Departments.query.filter_by(name=data_in['name']).first()
    assert res.name == data_in['name']
    assert res.location == data_in['location']
    assert res.phone == data_in['phone']
    result = f"{res.name}, {res.location}, {res.phone}"
    assert result == data_out
    db.session.delete(res)
    db.session.commit()




from main import create_dep, app, db
