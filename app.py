# pyrefly: ignore [missing-import]
from flask import Flask , request , render_template, jsonify
import copy
# pyrefly: ignore [missing-import]
from pymongo import MongoClient
import os 
import uuid
from datetime import datetime 
from config import MONGO_URI
app = Flask(__name__)   


client = MongoClient(MONGO_URI)
TOURNEMENT_NAME = "__"

# Function to get the current collection dynamically
def get_matches_collection():
    # Sanitize the tournament name: replace spaces with underscores for MongoDB compatibility
    sanitized_name = TOURNEMENT_NAME.replace(" ", "_")
    db_name = f'cricket_db_{sanitized_name}'
    return client[db_name]['matches']




# Generate a dynamic match ID based on timestamp and a short UUID
def generate_match_id():
    return f"match_{datetime.now().strftime('%Y%m%d_%H%M')}_{str(uuid.uuid4())[:4]}"

MATCH_ID = generate_match_id()

@app.route('/')
@app.route('/home', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/scoreboard')
def scoreboard():
    return render_template('scoreboard.html')

def initialInningData():
    return {
        'tournementName':'__',
        'teamName': 'Team-Name',
        'totalRuns': 0,
        'wickets': 0,
        'overs': 0.0,
        'batsmen': [
            { 'name': 'Batsman-1-', 'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0, 'isStriker': True },
            { 'name': 'Batsman-2-', 'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0, 'isStriker': False }
        ],
        'availableBatsmen': [],
        'dismissedBatsmen': [],
        'bowler': [{ 'name': 'Bowler', 'runs': 0, 'overs': 0, 'wickets': 0, 'economy': '0.00', 'isBowler': True }],
        'currentOver': [],
        'pastOver': [],
        'extraRuns': 0,
        'runRate': "0.00",
        'projectedScore': "--",
        'remainingRuns': 0,
        'remainingBalls': 0,
        'rrr': "0.00",
        'totalOvers': 0,
        'commentary': [],
        'fallOfWickets': [],
        'ballsPerOver': 6,
        'playersPerTeam':11
    }

session_state = {
    'inning1Data': initialInningData(),
    'inning2Data': initialInningData(),
    'currentInning': 1,
    'tournementName':TOURNEMENT_NAME
}

history_stack = []

# def save_to_db():
#     """Saves the current session_state to MongoDB"""
#     try:
#         matches_collection.update_one(
#             {"_id": MATCH_ID},
#             {"$set": session_state},
#             upsert=True
#         )
#     except Exception as e:
#         print(f"Error saving to MongoDB: {e}")

def save_to_db():
    """Saves the current session_state to MongoDB using the current tournament database"""
    global TOURNEMENT_NAME
    try:
        # Use the dynamic collection getter
        sanitized_name = TOURNEMENT_NAME.replace(" ", "_")
        db_name = f'cricket_db_{sanitized_name}'
        coll = get_matches_collection()

        
        print(f"--- ATTEMPTING SAVE ---")
        print(f"Tournament: {TOURNEMENT_NAME}")
        print(f"Database: {db_name}")
        print(f"Match ID: {MATCH_ID}")
        
        result = coll.update_one(
            {"_id": MATCH_ID},
            {"$set": session_state},
            upsert=True
        )
        
        if result.upserted_id:
            print(f"SUCCESS: Created new match document in {db_name}")
        else:
            print(f"SUCCESS: Updated existing match document in {db_name}")
            
    except Exception as e:
        print(f"ERROR saving to MongoDB: {e}")


    

# def load_from_db():
#     """Loads the session_state from MongoDB on startup"""
#     global session_state
#     try:
#         saved_state = matches_collection.find_one({"_id": MATCH_ID})
#         if saved_state:
#             # Remove the MongoDB internal ID before updating local state
#             saved_state.pop('_id', None)
#             session_state = saved_state
#             print("Successfully loaded match data from MongoDB")
#     except Exception as e:
#         print(f"Error loading from MongoDB: {e}")


def load_from_db():
    """Loads the session_state from MongoDB on startup"""
    global session_state
    try:
        # Use the dynamic collection getter
        coll = get_matches_collection()
        saved_state = coll.find_one({"_id": MATCH_ID})
        if saved_state:
            # Remove the MongoDB internal ID before updating local state
            saved_state.pop('_id', None)
            session_state = saved_state
            print(f"Successfully loaded match data from DB: cricket_db_{TOURNEMENT_NAME}")
    except Exception as e:
        print(f"Error loading from MongoDB: {e}")


# Load data when the server starts
load_from_db()

def save_to_history():
    global session_state, history_stack
    # Save a deep copy of the current state
    history_stack.append(copy.deepcopy(session_state))
    # Limit history to last 100 actions (roughly 15+ overs)
    if len(history_stack) > 100: 
        history_stack.pop(0)

@app.route('/undo', methods=['POST'])
def undo():
    global session_state, history_stack
    if not history_stack:
        return jsonify({'status': 'error', 'message': 'No more undo levels'}), 400
    
    session_state = history_stack.pop()
    save_to_db()
    return jsonify({
        'status': 'success',
        'data': {
            'matchData': get_match_data(),
            'currentInning': session_state['currentInning'],
            'inning1Data': session_state['inning1Data'],
            'inning2Data': session_state['inning2Data']
        }
    }), 200
# We use a property/helper to get current matchData
def get_match_data():
    if session_state['currentInning'] == 1:
        return session_state['inning1Data']
    else:
        return session_state['inning2Data']


def incrementOvers(overs):
    whole = int(overs)
    balls = round((overs - whole) * 10)
    if balls == (session_state['inning1Data']['ballsPerOver']-1):
        return float(whole + 1)
    else:
        return float(f"{whole}.{balls + 1}")


@app.route('/syncSession', methods=['POST'])
def syncSession():
    global session_state
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    session_state.update(data)
    save_to_db()
    return jsonify({'status': 'success', 'data': session_state}), 200

@app.route('/addRuns', methods=['POST'])
def addRuns():
    save_to_history()
    global session_state
    data = request.get_json()
    runs = data.get('runs') 
    
    match_data = get_match_data()

    # add total runs
    if runs is None:
        return jsonify({'error': 'No runs provided'}), 400
    match_data['totalRuns'] += runs

    # batsman section 
    if match_data['batsmen'][0]['isStriker']:
        match_data['batsmen'][0]['runs'] += runs
        if runs == 4:
            match_data['batsmen'][0]['fours'] += 1
        elif runs == 6:
            match_data['batsmen'][0]['sixes'] += 1
        match_data['batsmen'][0]['balls'] += 1
    else:
        match_data['batsmen'][1]['runs'] += runs
        if runs == 4:
            match_data['batsmen'][1]['fours'] += 1
        elif runs == 6:
            match_data['batsmen'][1]['sixes'] += 1
        match_data['batsmen'][1]['balls'] += 1

    # strikerSwapping
    if(runs == 1 or runs==3 or runs==5):
        if match_data['batsmen'][0]['isStriker']:
            match_data['batsmen'][0]['isStriker'] = False
            match_data['batsmen'][1]['isStriker'] = True
        else:
            match_data['batsmen'][1]['isStriker'] = False
            match_data['batsmen'][0]['isStriker'] = True

    # incrementOvers
    is_bye_on_nb = data.get('is_bye_on_nb', False)
    if is_bye_on_nb is False:  
        match_data['overs'] = incrementOvers(match_data['overs'])

    # bowler section
    match_data['bowler'][0]['runs'] += runs
    if is_bye_on_nb is False: 
        match_data['bowler'][0]['overs'] = incrementOvers(match_data['bowler'][0]['overs'])

    # current over tracking
    match_data['currentOver'].append(runs)
    
    # commentary
    over_num = match_data['overs']
    striker = match_data['batsmen'][0]['name'] if match_data['batsmen'][0]['isStriker'] else match_data['batsmen'][1]['name']
    commentary_text = f"{over_num} {match_data['bowler'][0]['name']} to {striker}, {runs} run(s)"
    match_data['commentary'].insert(0, commentary_text)

    # Over completion logic
    if match_data['overs'] == float(int(match_data['overs'])):
        match_data['currentOver'] = []

    save_to_db()

    return jsonify({
        'status': 'success', 
        'data': {
            'matchData': match_data,
            'currentInning': session_state['currentInning'],
            'inning1Data': session_state['inning1Data'],
            'inning2Data': session_state['inning2Data']
        }
    }), 200

@app.route('/addWicket', methods=['POST'])
def addWicket():
    save_to_history()
    global session_state
    data = request.get_json()
    wicket_type = data.get('wicket_type', 'bowled') # default
    runs_on_wicket = data.get('runs', 0)
    
    match_data = get_match_data()
    
    # Update score
    match_data['totalRuns'] += runs_on_wicket
    match_data['wickets'] += 1
    
    # Update batsman
    striker_idx = 0 if match_data['batsmen'][0]['isStriker'] else 1
    out_batsman = match_data['batsmen'][striker_idx]
    out_batsman['runs'] += runs_on_wicket
    out_batsman['balls'] += 1
    
    match_data['dismissedBatsmen'].append(out_batsman)
    
    # current over tracking
    match_data['currentOver'].append('W')
    
    # commentary
    over_num = match_data['overs']
    striker_name = out_batsman['name']
    commentary_text = f"{over_num} {match_data['bowler'][0]['name']} to {striker_name}, WICKET! ({wicket_type})"
    match_data['commentary'].insert(0, commentary_text)

    # fall of wickets
    fow_entry = {
        'wicket_num': match_data['wickets'],
        'runs': match_data['totalRuns'],
        'overs': match_data['overs'],
        'batsman': striker_name
    }
    match_data['fallOfWickets'].append(fow_entry)
    
    # Update bowler
    match_data['bowler'][0]['wickets'] += 1
    match_data['bowler'][0]['runs'] += runs_on_wicket
    
    # Increment Over if valid ball
    is_invalid = data.get('is_invalid', False)  
    
    if not is_invalid : 
        match_data['overs'] = incrementOvers(match_data['overs'])
        match_data['bowler'][0]['overs'] = incrementOvers(match_data['bowler'][0]['overs'])

        # Over completion logic
        if match_data['overs'] == float(int(match_data['overs'])):
            match_data['currentOver'] = []

    save_to_db()

    return jsonify({
        'status': 'success',
        'data': {
            'matchData': match_data,
            'currentInning': session_state['currentInning'],
            'inning1Data': session_state['inning1Data'],
            'inning2Data': session_state['inning2Data']
        }
    }), 200

@app.route('/setNewBatsman', methods=['POST'])
def setNewBatsman():
    save_to_history()
    global session_state
    data = request.get_json()
    new_batsman_name = data.get('batsmanName')
    
    match_data = get_match_data()
    
    striker_idx = 0 if match_data['batsmen'][0]['isStriker'] else 1
    
    # Replace the out batsman with new one
    match_data['batsmen'][striker_idx] = {
        'name': new_batsman_name,
        'runs': 0,
        'balls': 0,
        'fours': 0,
        'sixes': 0,
        'isStriker': True
    }
    
    # Remove from available
    if new_batsman_name in match_data['availableBatsmen']:
        match_data['availableBatsmen'].remove(new_batsman_name)
    
    save_to_db()
        
    return jsonify({
        'status': 'success',
        'data': {
            'matchData': match_data,
            'currentInning': session_state['currentInning'],
            'inning1Data': session_state['inning1Data'],
            'inning2Data': session_state['inning2Data']
        }
    }), 200


    

# @app.route('/addWicket', methods=['POST'])
# def addWicket():
#     global session_state
#     session_state['matchData']['wickets'] += 1
#     return jsonify({'status': 'success', 'data': session_state}), 200

# @app.route('/addOver', methods=['POST'])
# def addOver():
#     global session_state
#     session_state['matchData']['overs'] += 0.1
#     if(session_state['matchData']['overs'] >= 0.7):
#         session_state['matchData']['overs'] = 1.0 
#         session_state['matchData']['bowler'][0]['overs'] += 1
#     return jsonify({'status': 'success', 'data': session_state}), 200


@app.route('/getMatch', methods=['GET'])
def getMatch():
    return jsonify({
        'tournementName':TOURNEMENT_NAME,
        'match_id': MATCH_ID,
        'matchData': get_match_data(),
        'currentInning': session_state['currentInning'],
        'inning1Data': session_state['inning1Data'],
        'inning2Data': session_state['inning2Data']
    }), 200

@app.route('/newMatch', methods=['POST'])
def newMatch():
    save_to_history()
    global session_state, MATCH_ID, TOURNEMENT_NAME
    # Generate a new dynamic ID for the new match
    MATCH_ID = generate_match_id()
    session_state['inning1Data'] = initialInningData()
    session_state['inning2Data'] = initialInningData()
    session_state['currentInning'] = 1
    session_state['tournementName'] = TOURNEMENT_NAME
    save_to_db()
    return jsonify({
        'status': 'success',
        'match_id': MATCH_ID,
        'tournementName':TOURNEMENT_NAME,
        'data': {
            'matchData': get_match_data(),
            'currentInning': session_state['currentInning'],
            'inning1Data': session_state['inning1Data'],
            'inning2Data': session_state['inning2Data']
        }
    }), 200

@app.route('/setPlayers', methods=['POST'])
def setPlayers():
    save_to_history()
    global session_state,TOURNEMENT_NAME
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    inning = data.get('inning', 1)
    session_state['currentInning'] = inning
    match_data = get_match_data()
    
    if 'tournementName' in data:
        new_name = data['tournementName']
        print(f"DEBUG: Setting TOURNEMENT_NAME to '{new_name}'")
        match_data['tournementName'] = new_name
        session_state['tournementName'] = new_name
        TOURNEMENT_NAME = new_name

    if 'teamName' in data:
        match_data['teamName'] = data['teamName']
    if 'totalOvers' in data:
        match_data['totalOvers'] = data['totalOvers']
    if 'batsmen' in data:
        match_data['batsmen'] = data['batsmen']
    if 'availableBatsmen' in data:
        match_data['availableBatsmen'] = data['availableBatsmen']

    if 'playersPerTeam' in data:
        match_data['playersPerTeam'] = data['playersPerTeam']
    if 'ballsPerOver' in data:
        match_data['ballsPerOver'] = data['ballsPerOver']

    save_to_db()
        
    return jsonify({
        'status': 'success',
        'data': {
            'matchData': get_match_data(),
            'currentInning': session_state['currentInning'],
            'inning1Data': session_state['inning1Data'],
            'inning2Data': session_state['inning2Data']
        }
    }), 200
    
@app.route('/addExtra', methods=['POST'])
def addExtra():
    save_to_history()
    global session_state
    data = request.get_json()
    extra_type = data.get('extra_type')
    runs = data.get('runs', 0)
    is_bye_on_nb = data.get('is_bye_on_nb', False)
    
    match_data = get_match_data()
    
    extra_runs_to_add = 0
    batsman_runs = 0
    ball_counts = True
    
    if extra_type == 'wide':
        extra_runs_to_add = 1 + runs
        ball_counts = False
        match_data['currentOver'].append(f"{runs}w" if runs > 0 else "w")
    elif extra_type == 'noball':
        extra_runs_to_add = 1
        if is_bye_on_nb:
            extra_runs_to_add += runs
        else:
            batsman_runs = runs
        ball_counts = False
        match_data['currentOver'].append(f"{runs}nb" if runs > 0 else "nb")
    elif extra_type == 'bye':
        extra_runs_to_add = runs
        match_data['currentOver'].append(f"{runs}b")
    elif extra_type == 'legbye':
        extra_runs_to_add = runs
        match_data['currentOver'].append(f"{runs}lb")

    # Update team score
    match_data['totalRuns'] += (extra_runs_to_add + batsman_runs)
    match_data['extraRuns'] += extra_runs_to_add
    
    # Update batsman if runs off the bat (only for No Ball or legal ball)
    if batsman_runs > 0:
        striker_idx = 0 if match_data['batsmen'][0]['isStriker'] else 1
        match_data['batsmen'][striker_idx]['runs'] += batsman_runs
        if batsman_runs == 4: match_data['batsmen'][striker_idx]['fours'] += 1
        if batsman_runs == 6: match_data['batsmen'][striker_idx]['sixes'] += 1

    # Wide/No Ball also gives batsman 1 ball faced? usually no, but No Ball might? 
    # In most cricket formats:
    # Wide: Ball not faced, ball not counted in over.
    # No Ball: Ball faced, ball not counted in over.
    if extra_type != 'wide' and not (extra_type == 'noball' and is_bye_on_nb):
        striker_idx = 0 if match_data['batsmen'][0]['isStriker'] else 1
        match_data['batsmen'][striker_idx]['balls'] += 1

    # Update bowler
    match_data['bowler'][0]['runs'] += (extra_runs_to_add + batsman_runs)
    # Note: Wide/No Ball extras (the +1) are charged to bowler. 
    # Byes/Leg Byes are NOT charged to bowler.
    if extra_type in ['bye', 'legbye']:
        match_data['bowler'][0]['runs'] -= extra_runs_to_add

    if ball_counts:
        match_data['overs'] = incrementOvers(match_data['overs'])
        match_data['bowler'][0]['overs'] = incrementOvers(match_data['bowler'][0]['overs'])
        
        # Over completion logic
        if match_data['overs'] == float(int(match_data['overs'])):
            match_data['currentOver'] = []

    save_to_db()

    # commentary
    striker_name = match_data['batsmen'][0]['name'] if match_data['batsmen'][0]['isStriker'] else match_data['batsmen'][1]['name']
    match_data['commentary'].insert(0, f"{match_data['overs']} {match_data['bowler'][0]['name']} to {striker_name}, {extra_type.upper()} ({extra_runs_to_add + batsman_runs} runs)")

    return jsonify({
        'status': 'success',
        'data': {
            'matchData': match_data,
            'currentInning': session_state['currentInning'],
            'inning1Data': session_state['inning1Data'],
            'inning2Data': session_state['inning2Data']
        }
    }), 200

@app.route('/matchOverview', methods=['GET'])
def matchOverview():
    return jsonify({
        'inning1Data': session_state['inning1Data'],
        'inning2Data': session_state['inning2Data']
    }), 200

@app.route('/swapInning', methods=['POST'])
def swapInning():
    save_to_history()
    global session_state
    session_state['currentInning'] = 2 if session_state['currentInning'] == 1 else 1
    save_to_db()
    return jsonify({
        'status': 'success',
        'data': {
            'matchData': get_match_data(),
            'currentInning': session_state['currentInning'],
            'inning1Data': session_state['inning1Data'],
            'inning2Data': session_state['inning2Data']
        }
    }), 200



@app.route('/setBowler', methods=['POST'])
def setBowler():
    save_to_history()
    global session_state
    data = request.get_json()
    bowler_name = data.get('bowlerName')
    
    match_data = get_match_data()
    
    current_bowler = match_data['bowler'][0]
    if current_bowler['overs'] > 0 or current_bowler['runs'] > 0 or current_bowler['wickets'] > 0:
        match_data['pastOver'].append([dict(current_bowler)])
        
    existing_bowler_idx = -1
    for i, bo_arr in enumerate(match_data['pastOver']):
        if bo_arr[0]['name'].lower() == bowler_name.lower():
            existing_bowler_idx = i
            break
            
    if existing_bowler_idx != -1:
        past_stats = match_data['pastOver'].pop(existing_bowler_idx)[0]
        match_data['bowler'] = [{
            'name': past_stats['name'],
            'overs': past_stats.get('overs', 0),
            'runs': past_stats.get('runs', 0),
            'wickets': past_stats.get('wickets', 0),
            'economy': past_stats.get('economy', '0.00'),
            'isBowler': True
        }]
    else:
        match_data['bowler'] = [{
            'name': bowler_name,
            'overs': 0,
            'runs': 0,
            'wickets': 0,
            'economy': '0.00',
            'isBowler': True
        }]
        
    save_to_db()
        
    return jsonify({
        'status': 'success',
        'data': {
            'matchData': match_data,
            'currentInning': session_state['currentInning'],
            'inning1Data': session_state['inning1Data'],
            'inning2Data': session_state['inning2Data']
        }
    }), 200


@app.route('/setStriker', methods=['POST'])
def setStriker():
    save_to_history()
    global session_state
    data = request.get_json()
    index = data.get('index')
    
    match_data = get_match_data()
    
    if 0 <= index < len(match_data['batsmen']):
        for i, b in enumerate(match_data['batsmen']):
            b['isStriker'] = (i == index)
    
    save_to_db()
            
    return jsonify({
        'status': 'success',
        'data': {
            'matchData': match_data,
            'currentInning': session_state['currentInning'],
            'inning1Data': session_state['inning1Data'],
            'inning2Data': session_state['inning2Data']
        }
    }), 200

if __name__ == '__main__': 
    app.run(debug=True, port=5000)
    print(session_state) 