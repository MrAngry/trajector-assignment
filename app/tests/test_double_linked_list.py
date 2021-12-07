import pytest

from main import app
from models.item import Item


def add_x_items(client, x):
    test_item = {
        "url"  : "https://www.some.domain.com/product/1",
        "price": 1.0,
    }

    url = app.url_path_for("create_item")
    for i in range(x):
        response = client.post(url, json=test_item)
        assert response.status_code == 201


async def get_items_ids_in_forward_order():
    result = []
    item = await Item.get(previous=None)
    while item.next_id != None:
        result.append(item.id)
        item = await Item.get(id=item.next_id)
    result.append(item.id)
    return result


async def get_items_ids_in_backward_order():
    result = []
    item = await Item.get(next=None)
    while item.previous_id != None:
        result.append(item.id)
        item = await Item.get(id=item.previous_id)
    result.append(item.id)
    return result


@pytest.mark.asyncio
async def test_adding_order_is_correct(client):
    add_x_items(client, 4)
    expected_id_order = [4, 3, 2, 1]
    assert 4 == len(await Item.all())
    assert expected_id_order == await get_items_ids_in_forward_order()
    assert list(reversed(expected_id_order)) == await get_items_ids_in_backward_order()


@pytest.mark.asyncio
async def test_order_preserved_after_delete(client):
    add_x_items(client, 4)
    url = app.url_path_for("delete_item", item_id=3)
    client.delete(url)
    expected_id_order = [4, 2, 1]

    assert 3 == len(await Item.all())
    assert expected_id_order == await get_items_ids_in_forward_order()
    assert list(reversed(expected_id_order)) == await get_items_ids_in_backward_order()


@pytest.mark.asyncio
async def test_insert_after(client):
    add_x_items(client, 4)
    url = app.url_path_for("create_item")
    test_item = {
        "url"        : "https://www.some.domain.com/product/1",
        "price"      : 1.0,
        "previous_id": 3
    }

    client.post(url, json=test_item)
    expected_id_order = [4, 3, 5, 2, 1]

    assert 5 == len(await Item.all())
    assert expected_id_order == await get_items_ids_in_forward_order()
    assert list(reversed(expected_id_order)) == await get_items_ids_in_backward_order()


@pytest.mark.asyncio
async def test_insert_before(client):
    add_x_items(client, 4)
    url = app.url_path_for("create_item")
    test_item = {
        "url"    : "https://www.some.domain.com/product/1",
        "price"  : 1.0,
        "next_id": 3
    }

    client.post(url, json=test_item)
    expected_id_order = [4, 5, 3, 2, 1]

    assert 5 == len(await Item.all())
    assert expected_id_order == await get_items_ids_in_forward_order()
    assert list(reversed(expected_id_order)) == await get_items_ids_in_backward_order()


@pytest.mark.asyncio
async def test_move_item(client):
    add_x_items(client, 4)

    assert 4 == len(await Item.all())
    url = app.url_path_for("patch_item", item_id=2)
    test_item = {
        "url"    : "https://www.some.domain.com/product/1",
        "price"  : 1.0,
        "next_id": 3
    }
    client.patch(url, json=test_item)
    expected_id_order = [4, 2, 3, 1]

    assert expected_id_order == await get_items_ids_in_forward_order()
    assert list(reversed(expected_id_order)) == await get_items_ids_in_backward_order()


@pytest.mark.asyncio
async def test_filtering_by_tags_and_favorite(client):
    url = app.url_path_for("create_item")
    test_item = {
        "url"  : "https://www.some.domain.com/product/1",
        "price": 1.0,
        "tags" : ['tag_1']
    }
    client.post(url, json=test_item)

    test_item['tags'] = ['tag_2']
    test_item['is_favorite'] = True
    client.post(url, json=test_item)

    url = app.url_path_for("read_items")
    response = client.get(url, params={"tags": ['tag_1']})
    assert response.status_code == 200
    items = response.json()
    assert 1 == len(items)
    assert 'tag_1' in items[0]['tags']

    response = client.get(url, params={"is_favorite": True})
    assert response.status_code == 200
    items = response.json()
    assert 1 == len(items)
    assert True == items[0]['is_favorite']


