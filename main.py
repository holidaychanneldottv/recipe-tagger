from tagging import auto_tag_recipes, tag_recipe_by_id


if __name__ == "__main__":
    
    # tag all recipes based on keywords
    auto_tag_recipes()

    # provide a specific recipe ID to tag
    # tag_recipe_by_id(1)