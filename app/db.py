import os

# pyrefly: ignore [missing-import]
from pymongo import MongoClient

# Prefer the MONGO_URI environment variable (used in Docker/production) and
# fall back to the local, gitignored config.py (used for local dev without Docker).
MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    from config import MONGO_URI

client = MongoClient(MONGO_URI)


def get_matches_collection(tournament_name):
    # Sanitize the tournament name: replace spaces with underscores for MongoDB compatibility
    sanitized_name = tournament_name.replace(" ", "_")
    db_name = f'cricket_db_{sanitized_name}'
    return client[db_name]['matches']


def save_to_db(tournament_name, match_id, session_state):
    """Saves session_state to MongoDB under the current tournament database"""
    try:
        sanitized_name = tournament_name.replace(" ", "_")
        db_name = f'cricket_db_{sanitized_name}'
        coll = get_matches_collection(tournament_name)

        print(f"--- ATTEMPTING SAVE ---")
        print(f"Tournament: {tournament_name}")
        print(f"Database: {db_name}")
        print(f"Match ID: {match_id}")

        result = coll.update_one(
            {"_id": match_id},
            {"$set": session_state},
            upsert=True
        )

        if result.upserted_id:
            print(f"SUCCESS: Created new match document in {db_name}")
        else:
            print(f"SUCCESS: Updated existing match document in {db_name}")

    except Exception as e:
        print(f"ERROR saving to MongoDB: {e}")


def load_from_db(tournament_name, match_id):
    """Loads a session_state document from MongoDB, if present"""
    try:
        coll = get_matches_collection(tournament_name)
        saved_state = coll.find_one({"_id": match_id})
        if saved_state:
            saved_state.pop('_id', None)
            print(f"Successfully loaded match data from DB: cricket_db_{tournament_name}")
        return saved_state
    except Exception as e:
        print(f"Error loading from MongoDB: {e}")
        return None
