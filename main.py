from fastapi import FastAPI, HTTPException

app = FastAPI()

# Sample recipes data
recipes = [
    {
        "id": 1,
        "name": "Spaghetti Carbonara",
        "ingredients": ["spaghetti", "egg", "parmesan", "bacon"],
    },
    {
        "id": 2,
        "name": "Chicken Tikka Masala",
        "ingredients": ["chicken", "tomato", "onion", "garlic"],
    },
    {
        "id": 3,
        "name": "Beef Stroganoff",
        "ingredients": ["beef", "onion", "garlic", "tomato"],
    },
    {
        "id": 4,
        "name": "Vegetable Stir Fry",
        "ingredients": ["vegetables", "soy sauce", "garlic", "ginger"],
    }
]

@app.get("/ping")
async def ping():
    return "pong"

@app.get("/recipes")
async def get_all_recipes():
    return {"recipes": recipes}

@app.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: int):
    for recipe in recipes:
        if recipe["id"] == recipe_id:
            return recipe
    raise HTTPException(status_code=404, detail="Recipe not found")