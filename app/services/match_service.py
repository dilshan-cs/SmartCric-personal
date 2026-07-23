import copy
import uuid
from datetime import datetime

from app import db
from app.models.match import initialInningData

TOURNEMENT_NAME = "__"


def generate_match_id():
    return f"match_{datetime.now().strftime('%Y%m%d_%H%M')}_{str(uuid.uuid4())[:4]}"


MATCH_ID = generate_match_id()

session_state = {
    'inning1Data': initialInningData(),
    'inning2Data': initialInningData(),
    'currentInning': 1,
    'tournementName': TOURNEMENT_NAME
}

history_stack = []


def set_tournament_name(name):
    global TOURNEMENT_NAME
    TOURNEMENT_NAME = name


def new_match_id():
    global MATCH_ID
    MATCH_ID = generate_match_id()
    return MATCH_ID


def reset_session_state():
    session_state['inning1Data'] = initialInningData()
    session_state['inning2Data'] = initialInningData()
    session_state['currentInning'] = 1
    session_state['tournementName'] = TOURNEMENT_NAME


def save_state():
    db.save_to_db(TOURNEMENT_NAME, MATCH_ID, session_state)


def load_state():
    """Loads the session_state from MongoDB on startup"""
    global session_state
    loaded = db.load_from_db(TOURNEMENT_NAME, MATCH_ID)
    if loaded:
        session_state = loaded


def save_to_history():
    """Saves a deep copy of the current state, capped at the last 100 actions (roughly 15+ overs)"""
    history_stack.append(copy.deepcopy(session_state))
    if len(history_stack) > 100:
        history_stack.pop(0)


def undo():
    global session_state
    if not history_stack:
        return False
    session_state = history_stack.pop()
    save_state()
    return True


def get_match_data():
    if session_state['currentInning'] == 1:
        return session_state['inning1Data']
    else:
        return session_state['inning2Data']


def incrementOvers(overs):
    whole = int(overs)
    balls = round((overs - whole) * 10)
    if balls == (session_state['inning1Data']['ballsPerOver'] - 1):
        return float(whole + 1)
    else:
        return float(f"{whole}.{balls + 1}")


# Load data when the server starts
load_state()
