from main import app, db
import pytest
import main


@pytest.mark.parametrize('data_in, data_out', [
        (
            {
                'customer': 3,
                'status': 'Новый',
                'type': "Платный",
                'descript': "поломка",
                'creator': 1,
                'serial': "666",
                'price': '13'},
            '3, Новый, Платный, поломка, 1, 666, 13'
        ),
        (
            {
                'customer': 4,
                'status': 'Готов',
                'type': "Гарантийный",
                'descript': "чистка",
                'creator': 5,
                'serial': "777"
            },
            '4, Готов, Гарантийный, чистка, 5, 777, 0'
        )
    ])
def test_create_order(data_in, data_out):
    resp = app.test_client().get("/create_ord", query_string=data_in)
    assert resp.status == '302 FOUND'
    res = main.Orders.query.filter_by(serial=data_in['serial']).first()
    assert res.customer == data_in['customer']
    assert res.status == data_in['status']
    assert res.type == data_in['type']
    assert res.descript == data_in['descript']
    assert res.creator == data_in['creator']
    assert res.serial == data_in['serial']
    result = f"{res.customer}, {res.status}, {res.type}, {res.descript}, {res.creator}, {res.serial}, {res.price}"
    assert result == data_out
    db.session.delete(res)
    db.session.commit()
