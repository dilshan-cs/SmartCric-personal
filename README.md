# SmartCric

A live cricket scoring web app. One person runs the scoreboard (runs, wickets, overs, extras, batsmen/bowler stats, commentary, fall of wickets) for a single match at a time, backed by MongoDB for persistence, with a public scoreboard view for spectators.

## Features

- Ball-by-ball scoring: runs, wickets (with dismissal type and fall-of-wicket tracking), wides, no-balls, byes, leg-byes
- Automatic strike rotation, over completion, and per-bowler stats (including switching back to a bowler's earlier spell)
- Two-innings match state with the ability to swap between them
- Undo (up to the last 100 actions) via an in-memory history stack
- Separate `/scoreboard` view for read-only display (e.g. on a second screen/projector)
- Match state is persisted to MongoDB, namespaced per tournament (`cricket_db_<tournament_name>`)

## Tech stack

- **Backend:** Flask 3 (Python 3.13), served by Gunicorn in Docker
- **Database:** MongoDB (tested against MongoDB Atlas)
- **Frontend:** server-rendered Jinja templates + vanilla JS/CSS (no build step)

## Project structure

```
app/
├── __init__.py          # create_app() factory, registers blueprints
├── db.py                 # MongoClient, get_matches_collection, save_to_db, load_from_db
├── models/
│   └── match.py           # initialInningData() — shape of one innings' state
├── services/
│   └── match_service.py   # session_state, history_stack, incrementOvers, get_match_data, ...
├── routes/
│   ├── pages.py            # '/', '/home', '/scoreboard'
│   └── match_routes.py     # all scoring API endpoints
├── templates/              # index.html (scorer UI), scoreboard.html (display view)
└── static/                 # style.css, script.js, SBG.jpeg

run.py                 # entry point — creates and runs the Flask app
config.py              # local-only, gitignored — holds MONGO_URI for non-Docker runs
requirements.txt
Dockerfile / docker-compose.yml / .dockerignore
.env.example           # template for the MONGO_URI env var used by Docker
```

## Prerequisites

- Python 3.13 (only for running without Docker)
- A MongoDB connection string (e.g. a free MongoDB Atlas cluster)
- Docker + Docker Compose (only for the Docker route)

## Configuration

The app needs one thing: a **`MONGO_URI`** MongoDB connection string. It's read in this order:

1. `MONGO_URI` environment variable (used by Docker/Compose)
2. `config.py` at the project root (used for local, non-Docker runs)

`config.py` and `.env` are both gitignored — neither is committed, and `config.py` is also excluded from the Docker build (`.dockerignore`) so the connection string never ends up baked into an image.

## Running with Docker (recommended)

1. Copy the env template and fill in your real connection string:
   ```
   cp .env.example .env
   # then edit .env and set MONGO_URI
   ```
2. Build and start:
   ```
   docker compose up --build
   ```
3. Open http://localhost:5000 (scorer view) and http://localhost:5000/scoreboard (display view).

Stop with `docker compose down`.

## Running locally without Docker

1. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   pip install -r requirements.txt
   ```
2. Create `config.py` in the project root:
   ```python
   MONGO_URI = "mongodb+srv://<username>:<password>@<cluster-host>/"
   ```
3. Run the app:
   ```
   python run.py
   ```
4. Open http://localhost:5000.

The dev server runs with `debug=True` on port 5000 — don't expose it directly to the internet; use the Docker/Gunicorn setup for anything beyond local testing.

## API overview

All endpoints operate on a single, global in-memory match (`session_state`), persisted to MongoDB after every mutation.

| Endpoint | Method | Purpose |
|---|---|---|
| `/newMatch` | POST | Start a fresh match (resets both innings) |
| `/setPlayers` | POST | Set tournament/team name, overs, players per team, batting order |
| `/addRuns` | POST | Record runs off the bat |
| `/addWicket` | POST | Record a wicket |
| `/addExtra` | POST | Record a wide / no-ball / bye / leg-bye |
| `/setNewBatsman` | POST | Bring in the next batsman after a wicket |
| `/setBowler` | POST | Change bowler (restores stats if they bowled earlier in the innings) |
| `/setStriker` | POST | Manually set which batsman is on strike |
| `/swapInning` | POST | Switch between innings 1 and 2 |
| `/undo` | POST | Revert the last scoring action |
| `/getMatch` | GET | Fetch the full current match state |
| `/matchOverview` | GET | Fetch both innings' data |
| `/syncSession` | POST | Bulk-overwrite session state (used for client resync) |

## Known limitations

- **Single match at a time, no multi-user sessions.** Match state is one global in-memory object, not per-browser or per-device — see [plan.txt](plan.txt) for the open question on supporting multiple concurrent devices/scorers.
- The Atlas credential currently in local `config.py` was committed to git history prior to it being gitignored; rotating that password is recommended if this repo is ever made public or shared.
