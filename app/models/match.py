def initialInningData():
    return {
        'tournementName': '__',
        'teamName': 'Team-Name',
        'totalRuns': 0,
        'wickets': 0,
        'overs': 0.0,
        'batsmen': [
            {'name': 'Batsman-1-', 'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0, 'isStriker': True},
            {'name': 'Batsman-2-', 'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0, 'isStriker': False}
        ],
        'availableBatsmen': [],
        'dismissedBatsmen': [],
        'bowler': [{'name': 'Bowler', 'runs': 0, 'overs': 0, 'wickets': 0, 'economy': '0.00', 'isBowler': True}],
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
        'playersPerTeam': 11
    }
