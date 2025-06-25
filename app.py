from fastapi import FastAPI, BackgroundTasks
from tagging import auto_tag_recipes, tag_recipe_by_id, bulk_insert_keywords

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Recipe Tagging API"}

@app.get("/upsert-keywords")
def upsert_keywords(background_tasks: BackgroundTasks):
    background_tasks.add_task(bulk_insert_keywords)
    return {"status": "Keywords upserted successfully"}

@app.get("/tag-all-recipes")
def tag_recipes(background_tasks: BackgroundTasks):
    background_tasks.add_task(auto_tag_recipes)
    return {"status": "Tagging started in the background"}

@app.get("/tag-recipe/{recipe_id}")
def tag_recipe(recipe_id: int, background_tasks: BackgroundTasks):
    background_tasks.add_task(tag_recipe_by_id, recipe_id)
    return {"status": f"Tagging started for recipe {recipe_id} in the background"}