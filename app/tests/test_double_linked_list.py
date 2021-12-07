import asyncio
import logging
from pdb import set_trace

import pytest
from asynctest import TestCase
from starlette.testclient import TestClient
from tortoise import Tortoise
from tortoise.contrib.test import getDBConfig, _init_db

from main import app
from models.item import Item


class TestSomething(TestCase):
    def setUp(self) -> None:

        _CONFIG = getDBConfig(app_label="models", modules=['models.item', 'models.tag'])
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(_init_db(_CONFIG))
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.loop.run_until_complete(Tortoise._drop_databases())

    def add_x_items(self,x):
        test_item = {
            "url"      : "https://www.some.domain.com/product/1",
            "price"    : 1.0,
        }

        url = app.url_path_for("create_item")
        for i in range(x):
            response = self.client.post(url, json=test_item)
            assert response.status_code == 201

    async def get_items_ids_in_forward_order(self):
        result = []
        item = await Item.get(previous=None)
        while item.next_id != None:
            result.append(item.id)
            item = await Item.get(id=item.next_id)
        result.append(item.id)
        return result

    async def get_items_ids_in_backward_order(self):
        result = []
        item = await Item.get(next=None)
        while item.previous_id != None:
            result.append(item.id)
            item = await Item.get(id=item.previous_id)
        result.append(item.id)
        return result

    @pytest.mark.asyncio
    async def test_adding_order_is_correct(self):
        self.add_x_items(4)
        expected_id_order = [4, 3, 2, 1]
        self.assertEqual(4, len(await Item.all()))
        self.assertListEqual(expected_id_order, await self.get_items_ids_in_forward_order())
        self.assertListEqual(list(reversed(expected_id_order)), await self.get_items_ids_in_backward_order())

    @pytest.mark.asyncio
    async def test_order_preserved_after_delete(self):
        self.add_x_items(4)
        url = app.url_path_for("delete_item",item_id=3)
        self.client.delete(url)
        expected_id_order = [4, 2, 1]

        self.assertEqual(3, len(await Item.all()))
        self.assertListEqual(expected_id_order, await self.get_items_ids_in_forward_order())
        self.assertListEqual(list(reversed(expected_id_order)), await self.get_items_ids_in_backward_order())

    @pytest.mark.asyncio
    async def test_insert_after(self):
        self.add_x_items(4)
        url = app.url_path_for("create_item")
        test_item = {
            "url"      : "https://www.some.domain.com/product/1",
            "price"    : 1.0,
            "previous_id": 3
        }

        self.client.post(url,json=test_item)
        expected_id_order = [4, 3, 5,  2, 1]

        self.assertEqual(5, len(await Item.all()))
        self.assertListEqual(expected_id_order, await self.get_items_ids_in_forward_order())
        self.assertListEqual(list(reversed(expected_id_order)), await self.get_items_ids_in_backward_order())

    @pytest.mark.asyncio
    async def test_insert_before(self):
        self.add_x_items(4)
        url = app.url_path_for("create_item")
        test_item = {
            "url"      : "https://www.some.domain.com/product/1",
            "price"    : 1.0,
            "next_id": 3
        }

        self.client.post(url,json=test_item)
        expected_id_order = [4, 5, 3,  2, 1]

        self.assertEqual(5, len(await Item.all()))
        self.assertListEqual(expected_id_order, await self.get_items_ids_in_forward_order())
        self.assertListEqual(list(reversed(expected_id_order)), await self.get_items_ids_in_backward_order())

    @pytest.mark.asyncio
    async def test_move_item(self):
        self.add_x_items(4)

        self.assertEqual(4, len(await Item.all()))
        url = app.url_path_for("patch_item",item_id=2)
        test_item = {
            "url"      : "https://www.some.domain.com/product/1",
            "price"    : 1.0,
            "next_id": 3
        }
        self.client.patch(url, json=test_item)
        expected_id_order = [4, 2, 3, 1]

        items = await Item.all()
        self.assertListEqual(expected_id_order, await self.get_items_ids_in_forward_order())
        self.assertListEqual(list(reversed(expected_id_order)), await self.get_items_ids_in_backward_order())
