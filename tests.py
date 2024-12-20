import asyncio
import json
import unittest

from fastapi.testclient import TestClient

import models
from database import Base, async_session, engine
from main import app


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def fill_data():
    async with async_session() as session:
        async with session.begin():
            session.add_all(
                [
                    models.Recipe(
                        title="Рецепт #1", description="Описание #1", ingredients="Ингредиенты #1", cooking_time=10
                    ),
                    models.Recipe(
                        title="Рецепт #2", description="Описание #2", ingredients="Ингредиенты #2", cooking_time=5
                    ),
                    models.Recipe(
                        title="Рецепт #3",
                        description="Описание #3",
                        ingredients="Ингредиенты #3",
                        cooking_time=15,
                        views_count=1,
                    ),
                ]
            )


class TestClientTestCase(unittest.TestCase):
    def setUp(self):
        asyncio.run(drop_models())
        asyncio.run(init_models())
        asyncio.run(fill_data())

        self.client = TestClient(app)

    def tearDown(self):
        asyncio.run(drop_models())

    def test_list(self):
        response = self.client.get("/recipes")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 3)
        self.assertDictEqual(data[0], {"title": "Рецепт #3", "cooking_time": 15, "id": 3, "views_count": 1})
        self.assertDictEqual(data[1], {"title": "Рецепт #2", "cooking_time": 5, "id": 2, "views_count": 0})
        self.assertDictEqual(data[2], {"title": "Рецепт #1", "cooking_time": 10, "id": 1, "views_count": 0})

    def test_detail_404(self):
        response = self.client.get("/recipes/5/")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content), {"message": "Рецепт с указанным идентификатором не найден"})

    def test_detail(self):
        response = self.client.get("/recipes/3/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            {
                "title": "Рецепт #3",
                "cooking_time": 15,
                "description": "Описание #3",
                "ingredients": "Ингредиенты #3",
                "id": 3,
            },
        )

    def test_create(self):
        data = {
            "title": "Рецепт #4",
            "description": "Описание #4",
            "ingredients": "Ингредиенты #4",
            "cooking_time": 75,
        }
        response = self.client.post("/recipes", data=json.dumps(data))

        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(json.loads(response.content), {"message": "Рецепт добавлен"})

        response = self.client.get("/recipes")
        self.assertEqual(len(json.loads(response.content)), 4)

    def test_create_422(self):
        data = {
            "title": "Рецепт #4",
            "description": "Описание #4",
            "ingredients": "Ингредиенты #4",
            "cooking_time": "Время готовки",
        }
        response = self.client.post("/recipes", data=json.dumps(data))

        self.assertEqual(response.status_code, 422)
        self.assertDictEqual(
            json.loads(response.content),
            {
                "detail": [
                    {
                        "input": "Время готовки",
                        "loc": ["body", "cooking_time"],
                        "msg": "Input should be a valid integer, unable to parse string " "as an integer",
                        "type": "int_parsing",
                    }
                ]
            },
        )
