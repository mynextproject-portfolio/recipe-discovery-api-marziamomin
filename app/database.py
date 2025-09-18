from typing import List
from app.models import Recipe

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