import os
import socket
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, event
from sqlalchemy.pool import NullPool
from collections import defaultdict
from keywords import (
    holiday_keywords,
    diet_keywords,
    cuisine_keywords,
    region_keywords,
    course_keywords,
)

orig_getaddrinfo = socket.getaddrinfo


def getaddrinfo_ipv4_only(*args, **kwargs):
    return [
        info for info in orig_getaddrinfo(*args, **kwargs) if info[0] == socket.AF_INET
    ]


socket.getaddrinfo = getaddrinfo_ipv4_only

load_dotenv()

DATABASE_URL = os.getenv("POSTGRES_URL")
DB_NAME = os.getenv("DB_NAME")
engine = create_engine(DATABASE_URL, poolclass=NullPool)


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
    with engine.begin() as conn:
        inserts = []

        for tag_type, tag_names in tags_to_insert.items():
            for name in tag_names:
                inserts.append({"name": name, "type": tag_type})

        if inserts:
            conn.execute(
                text(
                    f"""
                    INSERT INTO {DB_NAME}.tags (tag_name, tag_type)
                    VALUES (:name, :type)
                    ON CONFLICT DO NOTHING
                """
                ),
                inserts,
            )

    print("Tags inserted into tags table.")


# insert keywords into tag_keywords table
def get_all_tag_ids(conn):
    tag_ids = conn.execute(
        text(f"SELECT tag_id, tag_name, tag_type FROM {DB_NAME}.tags")
    ).mappings()
    tag_lookup = defaultdict(dict)
    for row in tag_ids:
        tag_lookup[row["tag_type"]][row["tag_name"]] = row["tag_id"]
    return tag_lookup


def bulk_insert_keywords():
    print("Inserting tags into tags table...")
    bulk_insert_tags()
    print("Inserting keywords into tag_keywords...")
    with engine.begin() as conn:
        tag_lookup = get_all_tag_ids(conn)

        inserts = []

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
                    print(
                        f"Tag '{tag_name}' with type '{tag_type}' not found in tags table."
                    )
                    continue

                for keyword in keywords:
                    inserts.append({"tag_id": tag_id, "keyword": keyword})

        if inserts:
            conn.execute(
                text(
                    f"""
                    INSERT INTO {DB_NAME}.tag_keywords (tag_id, keyword)
                    VALUES (:tag_id, :keyword)
                    ON CONFLICT DO NOTHING
                """
                ),
                inserts,
            )

    print("Keywords inserted into tag_keywords.")


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


def fetch_all_recipes(conn):
    result = conn.execute(
        text(f"SELECT recipe_id, recipe_name, instructions FROM {DB_NAME}.recipe")
    ).mappings()
    return result.fetchall()


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


def auto_tag_recipes():
    print("Auto-tagging recipes based on keywords...")
    with engine.begin() as conn:
        tag_map = fetch_all_tag_keywords(conn)
        recipes = fetch_all_recipes(conn)

        bulk_insert_list = []

        for recipe in recipes:
            content = f"{recipe['recipe_name']} {recipe['instructions']}".lower()
            for tag_id, keywords in tag_map.items():
                if any(kw in content for kw in keywords):
                    bulk_insert_list.append({"rid": recipe["recipe_id"], "tid": tag_id})

        if bulk_insert_list:
            conn.execute(
                text(
                    f"""
                    INSERT INTO {DB_NAME}.recipe_tags_mapping (recipe_id, tag_id)
                    VALUES (:rid, :tid)
                    ON CONFLICT DO NOTHING
                """
                ),
                bulk_insert_list,
            )

    print("Recipes auto-tagged based on keywords.")


def tag_recipe_by_id(recipe_id):
    with engine.begin() as conn:
        tag_map = fetch_all_tag_keywords(conn)
        recipe = conn.execute(
            text(
                f"SELECT recipe_name, instructions FROM {DB_NAME}.recipe WHERE recipe_id = :rid"
            ),
            {"rid": recipe_id},
        ).fetchone()

        if not recipe:
            print(f"Recipe with ID {recipe_id} not found.")
            return

        content = f"{recipe['recipe_name']} {recipe['instructions']}".lower()

        for tag_id, keywords in tag_map.items():
            if any(kw in content for kw in keywords):
                tag_recipe(conn, recipe_id, tag_id)
    print(f"Recipe {recipe_id} auto-tagged based on keywords.")
