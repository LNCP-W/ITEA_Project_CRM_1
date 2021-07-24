import pytest
import main
from main import app


@pytest.mark.parametrize('order_id, ', [(17, ), (94, ), (95, )])
def test_order(order_id):
    order = main.Orders.query.filter_by(id=order_id).first()
    d = [
        f'name="id"  value={order.id}',
        f'name="created"  value="{order.created.strftime("%d/%m/%Y, %H:%M")}"',
        f'name="creator" value="{order.creator}"',
        f'name="status" form="data">\n                    <option selected value="{order.status}"',
        f'name="type" form="data">\n                    <option selected value="{order.type}"',
        f'name="descript" title="Какая неисправность в устройства" value="{order.descript}"',
        f'input type="text" name="serial" title="Серийный номер устройства" value="{order.serial}"',
        f'name="price" value="{order.price}"',
        f'name="updated" value="{order.updated.strftime("%d/%m/%Y, %H:%M")}"'
    ]
    resp = app.test_client().get("/order", query_string={'id': order_id})
    html_string = resp.data.decode('utf-8')
    assert resp.status == '200 OK'
    for i in d:
        x = html_string.find(i)
        assert x != -1
