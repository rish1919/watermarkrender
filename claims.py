import random
import json
import os

CODES_FILE = "claimcodes.json"

def load_codes():
    if os.path.exists(CODES_FILE):
        with open(CODES_FILE, "r") as f:
            return json.load(f)
    return {"codes": [], "claimed": []}

def save_codes(data):
    with open(CODES_FILE, "w") as f:
        json.dump(data, f)

def generate_code():
    data = load_codes()
    code = str(random.randint(100000, 999999))
    data["codes"].append(code)
    save_codes(data)
    return code

def claim_code(user_id, code):
    data = load_codes()
    if code in data["codes"] and code not in data["claimed"]:
        data["claimed"].append(code)
        data[str(user_id)] = True
        save_codes(data)
        return True
    return False

def is_authorized(user_id):
    data = load_codes()
    return str(user_id) in data and data[str(user_id)] == True