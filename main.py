from flask import Flask, render_template, Response, request, redirect, session, abort, g
# import cv2
from src.forms import AuthForm, ForgotPasswordForm, VerifyTokenForm
from flask_misaka import Misaka
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from src.supabase import (
    supabase,
    user_context_processor,
    get_profile_by_user
)
from src.decorators import login_required, password_update_required, profile_required
from src.auth import auth


app = Flask(__name__, template_folder="./templates", static_folder="./static")
CORS(app)
Misaka(app)
socketio = SocketIO(app, cors_allowed_origins='*')

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b"c8af64a6a0672678800db3c5a3a8d179f386e083f559518f2528202a4b7de8f8"
app.context_processor(user_context_processor)
app.register_blueprint(auth)


@socketio.on('connect')
def handle_connect():
    print(f"A user connected to the server: {request.sid}")
    # Emit a 'join' event to all clients except the current one
    emit('event', {'type': 'join', 'from': request.sid, 'role': request.args.get('role')}, broadcast=True, include_self=False)

@socketio.on('event')
def handle_event(evt):
    print(f"A signaling event was sent: {evt.get('type')}")

    # Emit the event to a specific client (evt['to'])
    target_client = evt.get('to')
    if target_client:
        emit('event', evt, room=target_client)

@socketio.on('disconnect')
def handle_disconnect():
    print(f"A user is leaving: {request.sid}")
    # Emit a 'bye' event to all clients except the current one
    emit('event', {'type': 'bye', 'from': request.sid}, broadcast=True, include_self=False)


@app.teardown_appcontext
def close_supabase(e=None):
    g.pop("supabase", None)

@app.route('/')
def home():
    next = request.args.get("next")
    form = AuthForm()
    return render_template("auth/login.html", form=form, next=next)

@app.route('/stream-video')
@login_required
@password_update_required
@profile_required
def stream():
    session = supabase.auth.refresh_session
    print(session)
    return render_template('streaming.html')

@app.route('/watcher')
def watcher():
    session = supabase.auth.refresh_session
    print(session)
    return render_template('watcher.html')


@app.route("/dashboard")
@login_required
@password_update_required
@profile_required
def dashboard():
    profile = get_profile_by_user()
    return render_template("dashboard.html", profile=profile)

@app.route("/profile")
@login_required
@password_update_required
@profile_required
def profile():
    profile = get_profile_by_user()
    print(profile)
    return render_template("profile.html", profile=profile)



if __name__ == "__main__":
     socketio.run(app, host='0.0.0.0', port=5000, debug=True)
