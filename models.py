from typing import List, Union

from sqlalchemy import Column, Integer, String, select

from database import Base, async_session


class Recipe(Base):
    __tablename__ = "Recipe"

    id = Column(name="ID", type_=Integer, primary_key=True, index=True)
    title = Column(name="Название", type_=String)
    description = Column(name="Текстовое описание", type_=String)
    ingredients = Column(name="Список ингредиентов", type_=String)
    cooking_time = Column(name="Время готовки (в минутах)", type_=Integer, index=True)
    views_count = Column(name="Количество просмотров", type_=Integer, index=True, default=0)


async def get_recipe(idx: int) -> Union[Recipe, None]:
    async with async_session() as session:
        stmt = select(Recipe).where(Recipe.id == idx)
        res = await session.execute(stmt)
        if not (recipe := res.scalar_one_or_none()):
            return None

        recipe.views_count += 1
        await session.commit()

        return recipe


async def get_recipes() -> List[Recipe]:
    async with async_session() as session:
        stmt = select(Recipe).order_by(Recipe.views_count.desc(), Recipe.cooking_time)
        res = await session.execute(stmt)
        return res.scalars().all()


async def add_recipe(new_recipe: Recipe) -> None:
    async with async_session() as session:
        async with session.begin():
            session.add(new_recipe)
