from fastapi import FastAPI
from tagging import auto_tag_recipes, tag_recipe_by_id

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Recipe Tagging API"}


@app.get("/tag-all-recipes")
def tag_recipes():
    auto_tag_recipes()
    return {"status": "Tagging completed"}

@app.get("/tag-recipe/{recipe_id}")
def tag_recipe(recipe_id: int):
    tag_recipe_by_id(recipe_id)
    return {"status": f"Recipe {recipe_id} tagged successfully"}