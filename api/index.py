from flask import Flask, jsonify, request
import time

app = Flask(__name__)

saved_post = None
last_post_time = None
header_received_time = None
header_expiry_time = None

def open_get_post():
    global header_received_time, header_expiry_time
    header_received_time = time.time()
    header_expiry_time = header_received_time + 300  # 5 minutes

@app.route('/', methods=['POST'])
def handle_post():
    if 'X-Special-Header' in request.headers:
        open_get_post()  # Function to set header_received_time and header_expiry_time
        return jsonify({'message': 'Special header received. Access granted to /get_post for 5 minutes'}), 200
    else:
        return jsonify({'error': 'Special header missing. Access denied to /get_post'}), 403

@app.route('/get_post', methods=['GET'])
def get_saved_post():
    global header_received_time, header_expiry_time

    if saved_post is None:
        return jsonify({'error': 'No post saved yet'}), 404

    current_time = time.time()
    if header_received_time is not None and current_time <= header_expiry_time:
        return jsonify(saved_post), 200
    else:
        old = saved_post
        saved_post = None
        header_received_time = None
        header_expiry_time = None
        return jsonify(old), 200


if __name__ == '__main__':
    app.run()
