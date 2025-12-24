from app import create_app
from flask import render_template
from app.extentions.extentions import socketio
import app.socket.socket

app = create_app()


@app.errorhandler(403)
def forbidden(e):
    return render_template('error/403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template('error/500.html'), 500


if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)