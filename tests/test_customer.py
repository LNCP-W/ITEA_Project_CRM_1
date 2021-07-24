import pytest
import main
from main import app


@pytest.mark.parametrize('cust_id, ', [(33, ), (3, ), (22, ), (23, )])
def test_customer(cust_id):
    customer = main.Customers.query.filter_by(id=cust_id).first()
    d = [
        f'name="id" value={customer.id}',
        f'name="name" value="{customer.name}"',
        f'name="phone" value="{customer.phone}"'
    ]
    resp = app.test_client().get("/customer", query_string={'id': cust_id})
    html_string = resp.data.decode('utf-8')
    assert resp.status == '200 OK'
    for i in d:
        x = html_string.find(i)
        assert x != -1
