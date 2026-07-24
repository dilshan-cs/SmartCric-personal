# pyrefly: ignore [missing-import]
from flask import Blueprint, request, jsonify

from app.services import match_service

match_bp = Blueprint('match', __name__)


@match_bp.route('/undo', methods=['POST'])
def undo():
    if not match_service.undo():
        return jsonify({'status': 'error', 'message': 'No more undo levels'}), 400

    return jsonify({
        'status': 'success',
        'data': {
            'matchData': match_service.get_match_data(),
            'currentInning': match_service.session_state['currentInning'],
            'inning1Data': match_service.session_state['inning1Data'],
            'inning2Data': match_service.session_state['inning2Data']
        }
    }), 200


@match_bp.route('/syncSession', methods=['POST'])
def syncSession():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    match_service.session_state.update(data)
    match_service.save_state()
    return jsonify({'status': 'success', 'data': match_service.session_state}), 200


@match_bp.route('/addRuns', methods=['POST'])
def addRuns():
    match_service.save_to_history()
    data = request.get_json()
    runs = data.get('runs')

    match_data = match_service.get_match_data()

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
    if runs == 1 or runs == 3 or runs == 5:
        if match_data['batsmen'][0]['isStriker']:
            match_data['batsmen'][0]['isStriker'] = False
            match_data['batsmen'][1]['isStriker'] = True
        else:
            match_data['batsmen'][1]['isStriker'] = False
            match_data['batsmen'][0]['isStriker'] = True

    # incrementOvers
    is_bye_on_nb = data.get('is_bye_on_nb', False)
    if is_bye_on_nb is False:
        match_data['overs'] = match_service.incrementOvers(match_data['overs'])

    # bowler section
    match_data['bowler'][0]['runs'] += runs
    if is_bye_on_nb is False:
        match_data['bowler'][0]['overs'] = match_service.incrementOvers(match_data['bowler'][0]['overs'])

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

    match_service.save_state()

    return jsonify({
        'status': 'success',
        'data': {
            'matchData': match_data,
            'currentInning': match_service.session_state['currentInning'],
            'inning1Data': match_service.session_state['inning1Data'],
            'inning2Data': match_service.session_state['inning2Data']
        }
    }), 200


@match_bp.route('/addWicket', methods=['POST'])
def addWicket():
    match_service.save_to_history()
    data = request.get_json()
    wicket_type = data.get('wicket_type', 'bowled')  # default
    runs_on_wicket = data.get('runs', 0)

    match_data = match_service.get_match_data()

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

    if not is_invalid:
        match_data['overs'] = match_service.incrementOvers(match_data['overs'])
        match_data['bowler'][0]['overs'] = match_service.incrementOvers(match_data['bowler'][0]['overs'])

        # Over completion logic
        if match_data['overs'] == float(int(match_data['overs'])):
            match_data['currentOver'] = []

    match_service.save_state()

    return jsonify({
        'status': 'success',
        'data': {
            'matchData': match_data,
            'currentInning': match_service.session_state['currentInning'],
            'inning1Data': match_service.session_state['inning1Data'],
            'inning2Data': match_service.session_state['inning2Data']
        }
    }), 200


@match_bp.route('/setNewBatsman', methods=['POST'])
def setNewBatsman():
    match_service.save_to_history()
    data = request.get_json()
    new_batsman_name = data.get('batsmanName')

    match_data = match_service.get_match_data()

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

    match_service.save_state()

    return jsonify({
        'status': 'success',
        'data': {
            'matchData': match_data,
            'currentInning': match_service.session_state['currentInning'],
            'inning1Data': match_service.session_state['inning1Data'],
            'inning2Data': match_service.session_state['inning2Data']
        }
    }), 200


@match_bp.route('/getMatch', methods=['GET'])
def getMatch():
    return jsonify({
        'tournementName': match_service.TOURNEMENT_NAME,
        'match_id': match_service.MATCH_ID,
        'matchData': match_service.get_match_data(),
        'currentInning': match_service.session_state['currentInning'],
        'inning1Data': match_service.session_state['inning1Data'],
        'inning2Data': match_service.session_state['inning2Data']
    }), 200


@match_bp.route('/newMatch', methods=['POST'])
def newMatch():
    match_service.save_to_history()
    # Generate a new dynamic ID for the new match
    match_id = match_service.new_match_id()
    match_service.reset_session_state()
    match_service.save_state()
    return jsonify({
        'status': 'success',
        'match_id': match_id,
        'tournementName': match_service.TOURNEMENT_NAME,
        'data': {
            'matchData': match_service.get_match_data(),
            'currentInning': match_service.session_state['currentInning'],
            'inning1Data': match_service.session_state['inning1Data'],
            'inning2Data': match_service.session_state['inning2Data']
        }
    }), 200


@match_bp.route('/setPlayers', methods=['POST'])
def setPlayers():
    match_service.save_to_history()
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    inning = data.get('inning', 1)
    match_service.session_state['currentInning'] = inning
    match_data = match_service.get_match_data()

    if 'tournementName' in data:
        new_name = data['tournementName']
        print(f"DEBUG: Setting TOURNEMENT_NAME to '{new_name}'")
        match_data['tournementName'] = new_name
        match_service.session_state['tournementName'] = new_name
        match_service.set_tournament_name(new_name)

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

    match_service.save_state()

    return jsonify({
        'status': 'success',
        'data': {
            'matchData': match_service.get_match_data(),
            'currentInning': match_service.session_state['currentInning'],
            'inning1Data': match_service.session_state['inning1Data'],
            'inning2Data': match_service.session_state['inning2Data']
        }
    }), 200


@match_bp.route('/addExtra', methods=['POST'])
def addExtra():
    match_service.save_to_history()
    data = request.get_json()
    extra_type = data.get('extra_type')
    runs = data.get('runs', 0)
    is_bye_on_nb = data.get('is_bye_on_nb', False)

    match_data = match_service.get_match_data()

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
        if batsman_runs == 4:
            match_data['batsmen'][striker_idx]['fours'] += 1
        if batsman_runs == 6:
            match_data['batsmen'][striker_idx]['sixes'] += 1

    # Wide: Ball not faced, ball not counted in over.
    # No Ball: Ball faced, ball not counted in over.
    if extra_type != 'wide' and not (extra_type == 'noball' and is_bye_on_nb):
        striker_idx = 0 if match_data['batsmen'][0]['isStriker'] else 1
        match_data['batsmen'][striker_idx]['balls'] += 1

    # Update bowler
    match_data['bowler'][0]['runs'] += (extra_runs_to_add + batsman_runs)
    # Wide/No Ball extras (the +1) are charged to bowler.
    # Byes/Leg Byes are NOT charged to bowler.
    if extra_type in ['bye', 'legbye']:
        match_data['bowler'][0]['runs'] -= extra_runs_to_add

    if ball_counts:
        match_data['overs'] = match_service.incrementOvers(match_data['overs'])
        match_data['bowler'][0]['overs'] = match_service.incrementOvers(match_data['bowler'][0]['overs'])

        # Over completion logic
        if match_data['overs'] == float(int(match_data['overs'])):
            match_data['currentOver'] = []

    match_service.save_state()

    # commentary
    striker_name = match_data['batsmen'][0]['name'] if match_data['batsmen'][0]['isStriker'] else match_data['batsmen'][1]['name']
    match_data['commentary'].insert(0, f"{match_data['overs']} {match_data['bowler'][0]['name']} to {striker_name}, {extra_type.upper()} ({extra_runs_to_add + batsman_runs} runs)")

    return jsonify({
        'status': 'success',
        'data': {
            'matchData': match_data,
            'currentInning': match_service.session_state['currentInning'],
            'inning1Data': match_service.session_state['inning1Data'],
            'inning2Data': match_service.session_state['inning2Data']
        }
    }), 200


@match_bp.route('/matchOverview', methods=['GET'])
def matchOverview():
    return jsonify({
        'inning1Data': match_service.session_state['inning1Data'],
        'inning2Data': match_service.session_state['inning2Data']
    }), 200


@match_bp.route('/swapInning', methods=['POST'])
def swapInning():
    match_service.save_to_history()
    match_service.session_state['currentInning'] = 2 if match_service.session_state['currentInning'] == 1 else 1
    match_service.save_state()
    return jsonify({
        'status': 'success',
        'data': {
            'matchData': match_service.get_match_data(),
            'currentInning': match_service.session_state['currentInning'],
            'inning1Data': match_service.session_state['inning1Data'],
            'inning2Data': match_service.session_state['inning2Data']
        }
    }), 200


@match_bp.route('/setBowler', methods=['POST'])
def setBowler():
    match_service.save_to_history()
    data = request.get_json()
    bowler_name = data.get('bowlerName')

    match_data = match_service.get_match_data()

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

    match_service.save_state()

    return jsonify({
        'status': 'success',
        'data': {
            'matchData': match_data,
            'currentInning': match_service.session_state['currentInning'],
            'inning1Data': match_service.session_state['inning1Data'],
            'inning2Data': match_service.session_state['inning2Data']
        }
    }), 200


@match_bp.route('/setStriker', methods=['POST'])
def setStriker():
    match_service.save_to_history()
    data = request.get_json()
    index = data.get('index')

    match_data = match_service.get_match_data()

    if 0 <= index < len(match_data['batsmen']):
        for i, b in enumerate(match_data['batsmen']):
            b['isStriker'] = (i == index)

    match_service.save_state()

    return jsonify({
        'status': 'success',
        'data': {
            'matchData': match_data,
            'currentInning': match_service.session_state['currentInning'],
            'inning1Data': match_service.session_state['inning1Data'],
            'inning2Data': match_service.session_state['inning2Data']
        }
    }), 200
