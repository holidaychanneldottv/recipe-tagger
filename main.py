from tagging import auto_tag_recipes, tag_recipe_by_id


if __name__ == "__main__":
    print("Starting recipe tagging...")
    # tag all recipes based on keywords
    auto_tag_recipes()
