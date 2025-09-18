from fastapi import FastAPI, HTTPException, Response, status, Query
from pydantic import BaseModel
from typing import List

app = FastAPI()

class RecipeBase(BaseModel):
    title: str
    ingredients: List[str]
    steps: List[str]
    prepTime: str
    cookTime: str
    difficulty: str
    cuisine: str


class RecipeCreate(RecipeBase):
    pass


class Recipe(RecipeBase):
    id: int


# In-memory store that matches the expected JSON format
recipes: List[Recipe] = [
    Recipe(
        id=1,
        title="Spaghetti Carbonara",
        ingredients=["pasta", "eggs", "bacon", "cheese"],
        steps=["Cook pasta", "Mix eggs", "Combine all"],
        prepTime="10 minutes",
        cookTime="15 minutes",
        difficulty="Medium",
        cuisine="Italian",
    ),
    Recipe(
        id=2,
        title="Chicken Tikka Masala",
        ingredients=["chicken", "tomato", "onion", "garlic"],
        steps=["Marinate chicken", "Cook sauce", "Combine and simmer"],
        prepTime="20 minutes",
        cookTime="30 minutes",
        difficulty="Medium",
        cuisine="Indian",
    ),
]

next_id: int = 3

@app.get("/ping")
async def ping():
    return "pong"

@app.get("/recipes")
async def get_all_recipes():
    return {"recipes": [recipe.model_dump() for recipe in recipes]}

@app.get("/recipes/search")
async def search_recipes(q: str | None = Query(default=None)):
    if not q:
        return {"recipes": []}
    q_lower = q.lower()
    matches = [
        r.model_dump() for r in recipes 
        if q_lower in r.title.lower()    
    ]
    return {"recipes": matches}

@app.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: int):
    for recipe in recipes:
        if recipe.id == recipe_id:
            return recipe
    raise HTTPException(status_code=404, detail="Recipe not found")


@app.post("/recipes", status_code=status.HTTP_201_CREATED)
async def create_recipe(payload: RecipeCreate):
    global next_id
    new_recipe = Recipe(id=next_id, **payload.model_dump())
    recipes.append(new_recipe)
    next_id += 1
    return new_recipe


@app.put("/recipes/{recipe_id}")
async def update_recipe(recipe_id: int, payload: RecipeCreate):
    for index, recipe in enumerate(recipes):
        if recipe.id == recipe_id:
            updated = Recipe(id=recipe_id, **payload.model_dump())
            recipes[index] = updated
            return updated
    raise HTTPException(status_code=404, detail="Recipe not found")


@app.delete("/recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(recipe_id: int):
    for index, recipe in enumerate(recipes):
        if recipe.id == recipe_id:
            del recipes[index]
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail="Recipe not found")