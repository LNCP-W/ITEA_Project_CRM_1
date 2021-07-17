import pytest
import main
@pytest.mark.parametrize('data_in, data_out', [
        (
            {'name': 'Vasia', 'position': 'worker', 'phone': 65653, 'dep_id':1},
            'Vasia, worker, 65653, 1'
        ),
        (
            {'name': 'Kolia', 'position': 'boss', 'phone': 13666, 'dep_id':75},
            'Kolia, boss, 13666, 75'
        )
    ])
def test_create_emp(data_in, data_out):
    resp = app.test_client().get("/create_emp", query_string=data_in)
    assert resp.status == '302 FOUND'
    res = main.Employees.query.filter_by(name=data_in['name']).first()
    assert res.name == data_in['name']
    assert res.position == data_in['position']
    assert res.phone == data_in['phone']
    assert res.dep_id == data_in['dep_id']
    result = f"{res.name}, {res.position}, {res.phone}, {res.dep_id}"
    assert result == data_out
    db.session.delete(res)
    db.session.commit()




from main import create_dep, app, db
