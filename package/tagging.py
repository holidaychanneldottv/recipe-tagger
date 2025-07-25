import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from collections import defaultdict
from keywords import (
    holiday_keywords,
    diet_keywords,
    cuisine_keywords,
    region_keywords,
    course_keywords,
)
load_dotenv()

DATABASE_URL = os.getenv("POSTGRES_URL")
DB_NAME = os.getenv("DB_NAME")
engine = create_engine(DATABASE_URL, poolclass=NullPool)
print("Database URL:", DATABASE_URL)


def fetch_all_recipes(conn):
    result = conn.execute(
        text(f"SELECT recipe_id, recipe_name, instructions FROM {DB_NAME}.recipe")
    ).mappings()
    return result.fetchall()

def get_all_tag_ids(conn):
    tag_ids = conn.execute(
        text(f"SELECT tag_id, tag_name, tag_type FROM {DB_NAME}.tags")
    ).mappings()
    tag_lookup = defaultdict(dict)
    for row in tag_ids:
        tag_lookup[row["tag_type"]][row["tag_name"]] = row["tag_id"]
    return tag_lookup

def fetch_all_tag_keywords(conn):
    result = conn.execute(
        text(f"SELECT tag_id, keyword FROM {DB_NAME}.tag_keywords")
    ).mappings()

    tag_map = {}
    for row in result:
        tag_id = row["tag_id"]
        keyword = row["keyword"].lower()
        if tag_id not in tag_map:
            tag_map[tag_id] = set()
        tag_map[tag_id].add(keyword)

    return tag_map

# Tag - tag key words mapping


tags_to_insert = {
    "holiday": list(holiday_keywords.keys()),
    "diet": list(diet_keywords.keys()),
    "cuisine": list(cuisine_keywords.keys()),
    "region": list(region_keywords.keys()),
    "course": list(course_keywords.keys()),
}


# insert tags into the database
def bulk_insert_tags():
    print("Inserting tags into tags table...")
    values = []
    for tag_type, tag_names in tags_to_insert.items():
        for name in tag_names:
            safe_name = name.replace("'", "''")
            safe_type = tag_type.replace("'", "''")
            values.append(f"('{safe_name}', '{safe_type}')")

    if values:
        sql = f"""
            INSERT INTO {DB_NAME}.tags (tag_name, tag_type)
            VALUES {', '.join(values)}
            ON CONFLICT DO NOTHING;
        """
        with engine.begin() as conn:
            conn.execute(text(sql))

    print("Tags inserted into tags table.")


# insert keywords into tag_keywords table
def bulk_insert_keywords():
    print("Inserting keywords into tag_keywords...")
    with engine.begin() as conn:
        tag_lookup = get_all_tag_ids(conn)

        values = []

        for tag_type, tag_dict in [
            ("holiday", holiday_keywords),
            ("cuisine", cuisine_keywords),
            ("diet", diet_keywords),
            ("region", region_keywords),
            ("course", course_keywords),
        ]:
            for tag_name, keywords in tag_dict.items():
                tag_id = tag_lookup.get(tag_type, {}).get(tag_name)
                if not tag_id:
                    print(f"Tag '{tag_name}' with type '{tag_type}' not found in tags table.")
                    continue

                for keyword in keywords:
                    # Properly escape single quotes
                    safe_keyword = keyword.replace("'", "''")
                    values.append(f"({tag_id}, '{safe_keyword}')")

        if values:
            sql = f"""
                INSERT INTO {DB_NAME}.tag_keywords (tag_id, keyword)
                VALUES {', '.join(values)}
                ON CONFLICT DO NOTHING;
            """
            conn.execute(text(sql))

    print("Keywords inserted into tag_keywords.")

# tag all recipes based on keywords
def auto_tag_recipes():
    print("Auto-tagging recipes based on keywords")
    with engine.begin() as conn:
        startTime = time.time()
        conn.execute(text("SET statement_timeout TO '1200000';"))
        conn.execute(
            text(f"""
                INSERT INTO {DB_NAME}.recipe_tags_mapping (recipe_id, tag_id)
                SELECT
                    r.recipe_id,
                    k.tag_id
                FROM
                    {DB_NAME}.recipe r
                JOIN
                    {DB_NAME}.tag_keywords k
                ON
                    lower(r.recipe_name) ~* ('\\m' || lower(k.keyword) || '\\M')
                ON CONFLICT DO NOTHING;
            """)
        )
        endTime = time.time()
        print(f"Auto-tagged recipes in {endTime - startTime:.2f} seconds.")
    print("Recipes auto-tagged based on keywords.")

# tag a specific recipe by ID based on keywords
def tag_recipe(conn, recipe_id, tag_id):
    exists = conn.execute(
        text(
            f"""
        SELECT 1 FROM {DB_NAME}.recipe_tags_mapping WHERE recipe_id = :rid AND tag_id = :tid
    """
        ),
        {"rid": recipe_id, "tid": tag_id},
    ).first()

    if not exists:
        conn.execute(
            text(
                f"""
            INSERT INTO {DB_NAME}.recipe_tags_mapping (recipe_id, tag_id) VALUES (:rid, :tid)
        """
            ),
            {"rid": recipe_id, "tid": tag_id},
        )


def tag_recipe_by_id(recipe_id):
    with engine.begin() as conn:
        tag_map = fetch_all_tag_keywords(conn)
        recipe = conn.execute(
            text(
                f"SELECT recipe_name FROM {DB_NAME}.recipe WHERE recipe_id = :rid"
            ),
            {"rid": recipe_id},
        ).fetchone()

        if not recipe:
            print(f"Recipe with ID {recipe_id} not found.")
            return

        content = f"{recipe['recipe_name']}".lower()

        for tag_id, keywords in tag_map.items():
            if any(kw in content for kw in keywords):
                tag_recipe(conn, recipe_id, tag_id)
    print(f"Recipe {recipe_id} auto-tagged based on keywords.")

# 85198