from flask import Flask, request, jsonify
import time

app = Flask(__name__)

saved_post = None
last_post_time = None

@app.route('/', methods=['POST'])
def handle_post():
    global saved_post, last_post_time

    saved_post = request.get_json()
    last_post_time = time.time()  # Record the time of the last POST request
    return jsonify({'message': 'Post saved successfully'}), 200

@app.route('/get_post', methods=['GET'])
def get_saved_post():
    global saved_post, last_post_time

    if saved_post is None:
        return jsonify({'error': 'No post saved yet'}), 404

    current_time = time.time()
    if last_post_time is not None and current_time - last_post_time <= 2:
        return jsonify(saved_post), 200
    else:
        old = saved_post
        saved_post = None
        return jsonify(old), 200

if __name__ == '__main__':
    app.run(debug=True)
