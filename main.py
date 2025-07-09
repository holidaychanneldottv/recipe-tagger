from tagging import auto_tag_recipes,bulk_insert_keywords, bulk_insert_tags
import time


if __name__ == "__main__":
    start_time = time.time()

    bulk_insert_tags()
    bulk_insert_keywords()
    auto_tag_recipes()
    
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time} seconds")
