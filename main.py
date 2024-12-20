from typing import List, Sequence, Union

from fastapi import FastAPI, Path
from fastapi.responses import JSONResponse

import models
import schemas
from database import engine

app = FastAPI()


@app.on_event('startup')
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@app.post('/recipes', response_model=schemas.RecipeIn)
async def create(recipe: schemas.RecipeIn) -> JSONResponse:
    new_recipe = models.Recipe(**recipe.dict())
    await models.add_recipe(new_recipe=new_recipe)
    return JSONResponse(content={'message': 'Рецепт добавлен'}, status_code=201)


@app.get('/recipes', response_model=List[schemas.RecipeListOut])
async def recipes_list() -> Sequence[models.Recipe]:
    return await models.get_recipes()


@app.get('/recipes/{idx}', response_model=schemas.RecipeDetailOut)
async def detail(idx: int = Path(..., title='Идентификатор рецепта.', ge=0)) -> Union[models.Recipe, JSONResponse]:
    recipe = await models.get_recipe(idx=idx)
    if recipe:
        return recipe
    return JSONResponse(content={'message': 'Рецепт с указанным идентификатором не найден'}, status_code=404)
