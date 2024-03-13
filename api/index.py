import os
import requests
import json
from bs4 import BeautifulSoup
import random
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_user_games(ck):
    user_id = get_cookie_id(ck)
    if not user_id:
        return None
    url = f"https://games.roblox.com/v2/users/{user_id}/games"
    try:
        response = requests.get(url)
        response.raise_for_status()
        games_data = response.json().get("data", [])
        for game in games_data:
            root_place_id = game.get("rootPlace", {}).get("id")
            if root_place_id:
                return root_place_id
    except requests.RequestException as e:
        print(f"Error getting user games: {e}")
        return None

def generate_logic_game_name():
    prefixes = ["Brain", "Mind", "Logic", "Puzzle", "Cognitive", "Smart"]
    suffixes = ["Challenge", "Quest", "Adventure", "Maze", "Journey", "Solver"]
    digits = str(random.randint(1000, 9999))
    
    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)
    
    return f"{prefix}{suffix}{digits}"

# Function to get CSRF token
def get_csrf_token(k):
    cookies = {
        '.ROBLOSECURITY': k,
    }
    headers = {
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    }
    try:
        response = requests.get("https://www.roblox.com/home", cookies=cookies, headers=headers)
        response.raise_for_status()
        html = BeautifulSoup(response.text, "html.parser")
        csrf_tag = html.find("meta", {"name": "csrf-token"})
        csrf_token = csrf_tag["data-token"]
        return csrf_token
    except requests.RequestException as e:
        print(f"Error getting CSRF token: {e}")
        return None

# Function to update Roblox game
def update_roblox_game(kl, game_name):
    n = kl
    csrf_token = get_csrf_token(n)
    if not csrf_token:
        return
    cookies = {
        '.ROBLOSECURITY': n,
    }

    headers = {
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'x-csrf-token': csrf_token,
    }

    json_data = {
        'name': game_name,
        'description': 'This is your very first Roblox creation. Check it out, then make it your own with Roblox Studio!',
    }
    game_url = get_user_games(n)
    print(game_url)
    try:
        response = requests.patch('https://develop.roblox.com/v2/places/'+str(game_url), cookies=cookies, headers=headers, json=json_data)
        response.raise_for_status()
        game_url = f"https://www.roblox.com/games/{game_url}"
        with open("games.txt", "a") as file:
            file.write(game_url + "\n")
        print(response)
    except requests.RequestException as e:
        print(f"Error updating Roblox game: {e}")

# Function to read cookie from file
def read_cookie_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Cookie file not found at {file_path}")
        return None

# Function to get user ID from cookie
def get_cookie_id(cookie):
    cookies = {'.ROBLOSECURITY': cookie}
    headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'}
    
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    
    try:
        response = session.get('https://users.roblox.com/v1/users/authenticated', cookies=cookies, headers=headers, timeout=10) # Increase timeout here
        response.raise_for_status()
        data = response.json()
        kk = data['id']
        return kk
    except requests.RequestException as e:
        print(f"Error getting user ID: {e}")
        return None

# Function to upload RBXL
def do_upload(buffer, asset_id, cookie):
    url = f"https://data.roblox.com/Data/Upload.ashx?assetid={asset_id}"

    headers = {
        "Cookie": f".ROBLOSECURITY={cookie}",
        "User-Agent": "Roblox/WinInet",
        "Content-Type": "application/xml",
        "Accept": "application/json",
    }

    for _ in range(2):  # Retry once if a CSRF challenge is received
        try:
            response = requests.post(url, headers=headers, data=buffer)
            status = response.status_code

            if status == 403 and "X-CSRF-Token" in response.headers:
                headers["X-CSRF-Token"] = response.headers["X-CSRF-Token"]
                continue

            response.raise_for_status()

            print("Upload successful.")
            return response.json().get("TargetId")  # Return the game ID

        except requests.RequestException as e:
            print(f"Error during upload: {e}")

    print(f"Failed to upload. HTTP status code: {status}")
    print(response.text)
    return None

# Function to upload RBXL
def upload_rbxl(cookies, gm):
    game_urls = []
    for cookie in cookies:
        asset_id2 = get_user_games(cookie)
        if asset_id2 is None:
            continue
        update_roblox_game(cookie, gm)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        rbxl_path = os.path.join(script_dir, "test.rbxl")  # Replace with your actual RBXL filename

        with open(rbxl_path, "rb") as rbxl_file:
            rbxl_data = rbxl_file.read()
        
        try:
            game_id = do_upload(rbxl_data, asset_id2, cookie)
            if game_id:
                game_urls.append(f"https://www.roblox.com/games/{game_id}")
                print(f"Game ID {game_id} edited successfully.")
        except Exception as e:
            print(f"Error: {e}")
    return game_urls

@app.route('/upload', methods=['POST'])
def upload():
    game_namo = generate_logic_game_name()
    uploaded_files = request.files.getlist("files[]")
    cookies = request.files['cookies']
    if 'cookies' not in request.files:
        return jsonify({"message": "No cookies file provided"}), 400
    cookies_data = cookies.read().decode("utf-8").strip()
    if not cookies_data:
        return jsonify({"message": "Empty cookies file"}), 400
    cookies_list = cookies_data.split("\n")
    game_urls = upload_rbxl(cookies_list, game_namo)
    with open("game_urls.txt", "w") as file:
        for url in game_urls:
            file.write(url + "\n")
    return jsonify({"message": "Upload successful", "game_urls": game_urls})

if __name__ == '__main__':
    app.run(debug=True)
