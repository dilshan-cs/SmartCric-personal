from flask import Blueprint, render_template

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/')
@pages_bp.route('/home', methods=['GET'])
def index():
    return render_template('index.html')


@pages_bp.route('/scoreboard')
def scoreboard():
    return render_template('scoreboard.html')
