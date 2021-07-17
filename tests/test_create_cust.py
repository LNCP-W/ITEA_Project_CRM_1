import pytest
import main
from main import app, db

@pytest.mark.parametrize('data_in, data_out', [
        (
            {'name': 'first', 'phone': 3},
            'first, 3'
        ),
        (
            {'name': 'six', 'phone': 8},
            'six, 8'
        )
    ])
def test_create_customer(data_in, data_out):
    resp = app.test_client().get("/create_customer", query_string=data_in)
    assert resp.status == '302 FOUND'
    res = main.Customers.query.filter_by(name=data_in['name']).first()
    assert res.name == data_in['name']
    assert res.phone == data_in['phone']
    result = f"{res.name}, {res.phone}"
    assert result == data_out
    db.session.delete(res)
    db.session.commit()





