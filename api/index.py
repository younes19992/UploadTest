from flask import Flask, request, jsonify
import time

app = Flask(__name__)

saved_post = None
last_post_time = None
MAX_RETRIES = 3

def perform_post_save():
    global saved_post, last_post_time

    if saved_post is None:
        saved_post = request.get_json()
        last_post_time = time.time()  # Record the time of the last POST request
        return True
    else:
        raise Exception("Post already saved")

@app.route('/', methods=['GET', 'POST'])
def handle_post():
    retries = 0

    while retries < MAX_RETRIES:
        try:
            if request.method == 'POST':
                success = perform_post_save()
                if success:
                    return jsonify({'message': 'Post saved successfully'}), 200
        except Exception as e:
            print(f"Error occurred: {e}")
            retries += 1
            print(f"Retrying... ({retries}/{MAX_RETRIES})")
            time.sleep(1)  # Wait for 1 second before retrying

    return jsonify({'error': 'Failed to save post'}), 500

@app.route('/get_post', methods=['GET'])
def get_saved_post():
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
    app.run()
