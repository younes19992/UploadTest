from flask import Flask, jsonify, request
import time
import threading

app = Flask(__name__)

saved_post = None
header_received_time = None
header_expiry_time = None
is_get_post_open = False

def open_get_post():
    global header_received_time, header_expiry_time, is_get_post_open
    header_received_time = time.time()
    header_expiry_time = header_received_time + 180  # 3 minutes
    is_get_post_open = True

def close_get_post():
    global saved_post, header_received_time, header_expiry_time, is_get_post_open
    saved_post = None
    header_received_time = None
    header_expiry_time = None
    is_get_post_open = False

def start_timer():
    threading.Timer(180, close_get_post).start()  # Start a timer to close /get_post after 3 minutes

@app.route('/', methods=['POST'])
def handle_post():
    global is_get_post_open

    if 'Auth' in request.headers:
        open_get_post()  # Open /get_post route
        start_timer()  # Start the timer to close /get_post after 3 minutes
        return jsonify({'message': 'Special header received. /get_post is now open for 3 minutes'}), 200
    else:
        close_get_post()  # Close /get_post route
        return jsonify({'error': 'Special header missing. /get_post is closed'}), 403

@app.route('/get_post', methods=['GET'])
def get_saved_post():
    global saved_post, header_received_time, header_expiry_time, is_get_post_open

    if not is_get_post_open:
        return jsonify({'error': 'Access denied to /get_post. It is closed'}), 403

    if saved_post is None:
        return jsonify({'error': 'No post saved yet'}), 404

    current_time = time.time()
    if header_received_time is not None and current_time <= header_expiry_time:
        return jsonify(saved_post), 200
    else:
        close_get_post()  # Close /get_post route after 3 minutes
        return jsonify({'error': 'Access denied to /get_post. It is closed'}), 403

if __name__ == '__main__':
    app.run()
