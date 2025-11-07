from flask import Blueprint, render_template

test = Blueprint('test', __name__)

@test.route('/test')
def hello():
    return render_template('test.html')