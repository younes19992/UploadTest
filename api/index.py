from flask import Flask, jsonify, request
import time

app = Flask(__name__)

saved_post = None
header_received_time = None
header_expiry_time = None
is_get_post_open = False

def open_get_post():
    global header_received_time, header_expiry_time, is_get_post_open
    header_received_time = time.time()
    header_expiry_time = header_received_time + 300  # 5 minutes
    is_get_post_open = True

def close_get_post():
    global saved_post, header_received_time, header_expiry_time, is_get_post_open
    saved_post = None
    header_received_time = None
    header_expiry_time = None
    is_get_post_open = False

@app.route('/', methods=['POST'])
def handle_post():
    global is_get_post_open

    if 'X-Special-Header' in request.headers:
        open_get_post()  # Open /get_post route
        return jsonify({'message': 'Special header received. /get_post is now open for 5 minutes'}), 200
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
        close_get_post()  # Close /get_post route after 5 minutes
        old = saved_post
        return jsonify(old), 200

if __name__ == '__main__':
    app.run()
