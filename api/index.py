from flask import Flask, jsonify, request
import os
import psycopg2

app = Flask(__name__)

# Get PostgreSQL connection parameters from environment variables
postgres_url = os.getenv('POSTGRES_URL')
postgres_user = os.getenv('POSTGRES_USER')
postgres_password = os.getenv('POSTGRES_PASSWORD')
postgres_host = os.getenv('POSTGRES_HOST')
postgres_database = os.getenv('POSTGRES_DATABASE')

def connect_to_postgresql():
    try:
        connection = psycopg2.connect(
            user=postgres_user,
            password=postgres_password,
            host=postgres_host,
            port='5432',  # Assuming the default PostgreSQL port
            database=postgres_database,
        )
        return connection
    except psycopg2.Error as error:
        print("Error while connecting to PostgreSQL:", error)
        return None

@app.route('/', methods=['POST'])
def handle_post():
    data = request.get_json()
    command = data.get('command')

    if command:
        # Connect to PostgreSQL database
        connection = connect_to_postgresql()
        if connection:
            try:
                cursor = connection.cursor()

                # Example: Execute SQL command
                cursor.execute("INSERT INTO your_table (command) VALUES (%s);", (command,))
                connection.commit()

                cursor.close()
                connection.close()

                return jsonify({'message': 'Command saved successfully'}), 200

            except psycopg2.Error as error:
                print("Error executing SQL command:", error)
                connection.rollback()
                connection.close()
                return jsonify({'error': 'Failed to save command'}), 500

        else:
            return jsonify({'error': 'Failed to connect to database'}), 500
    else:
        return jsonify({'error': 'No command provided'}), 400

if __name__ == '__main__':
    app.run()
