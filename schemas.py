from pydantic import BaseModel


class BaseRecipe(BaseModel):
    title: str
    cooking_time: int


class RecipeIn(BaseRecipe):
    description: str
    ingredients: str


class RecipeListOut(BaseRecipe):
    id: int
    views_count: int

    class Config:
        orm_mode = True


class RecipeDetailOut(RecipeIn):
    id: int

    class Config:
        orm_mode = True
