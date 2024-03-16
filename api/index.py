from flask import Flask, jsonify, request
import sqlite3
import time

app = Flask(__name__)

# Connect to SQLite database
conn = sqlite3.connect('registrations.db')
cursor = conn.cursor()

# Create a table for registrations if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS registrations
                (id INTEGER PRIMARY KEY AUTOINCREMENT, command TEXT, timestamp INTEGER)''')
conn.commit()

def save_registration_command(command):
    timestamp = int(time.time())  # Get current timestamp
    cursor.execute('''INSERT INTO registrations (command, timestamp) VALUES (?, ?)''', (command, timestamp))
    conn.commit()

@app.route('/', methods=['POST'])
def handle_post():
    data = request.get_json()
    command = data.get('command')

    if command:
        save_registration_command(command)
        return jsonify({'message': 'Registration command saved successfully'}), 200
    else:
        return jsonify({'error': 'No command provided'}), 400

@app.route('/get_registration', methods=['GET'])
def get_registration_command():
    current_time = int(time.time())
    cursor.execute('''SELECT * FROM registrations WHERE ? - timestamp <= 300''', (current_time,))
    registrations = cursor.fetchall()

    if registrations:
        # Delete the registration commands that are older than 5 minutes
        cursor.execute('''DELETE FROM registrations WHERE ? - timestamp > 300''', (current_time,))
        conn.commit()
        
        return jsonify(registrations), 200
    else:
        return jsonify({'message': 'No recent registration commands'}), 404

if __name__ == '__main__':
    app.run()
