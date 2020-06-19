from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, emit, send

# initialize Flask
app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    """Serve the index HTML"""
    return render_template('indextest.html')

@socketio.on('create')
def on_create(data):
    """Create a game lobby"""
    gm = game.Info(
        size=data['size'],
        teams=data['teams'],
        dictionary=data['dictionary'])
    room = gm.game_id
    ROOMS[room] = gm
    join_room(room)
    emit('join_room', {'room': room})



@socketio.on('stop')
def on_stop():
    """Stops website from running"""
    socketio.stop()
if __name__ == '__main__':
    # socketio.setsockopt(socketio.SOL_SOCKET, socketio.SO_REUSEADDR, 1)
    socketio.run(app, debug=True)