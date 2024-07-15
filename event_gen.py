import os
import pandas as pd
import hashlib
import random
from datetime import datetime, timedelta, timezone
import json
import numpy as np
import uuid

# Load configuration
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

# Constants
FIRST_NAMES = [
    "James", "John", "Robert", "Michael", "William", "David", "Joseph", "Charles", "Thomas", "Daniel",
    "Matthew", "Anthony", "Donald", "Steven", "Paul", "Andrew", "Mark", "George", "Kenneth", "Joshua",
    "Edward", "Brian", "Kevin", "Ronald", "Timothy", "Jason", "Jeffrey", "Frank", "Gary", "Stephen",
    "Scott", "Eric", "Gregory", "Jeremy", "Jacob", "Patrick", "Jonathan", "Raymond", "Benjamin", "Nicholas",
    "Samuel", "Alexander", "Tyler", "Brandon", "Adam", "Harry", "Dennis", "Arthur", "Alan", "Nathan",
    "Justin", "Carl", "Ryan", "Louis", "Aaron", "Christian", "Jerry", "Henry", "Jose", "Douglas",
    "Keith", "Zachary", "Lawrence", "Willie", "Albert", "Terry", "Joe", "Ethan", "Jesse", "Bryan",
    "Billy", "Jordan", "Alberto", "Jesse", "Oscar", "Danny", "Philip", "Ralph", "Roy", "Eugene",
    "Randy", "Vincent", "Wayne", "Elijah", "Billy", "Isaac", "Victor", "Russell", "Max", "Randall",
    "Lloyd", "Walter", "Leonard", "Fernando", "Lester", "Bobby", "Darrell", "Billy", "Bradley", "Gary",
    "Roger", "Kyle", "Theodore", "Tommy", "Larry", "Javier"
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson",
    "Martinez", "Anderson", "Taylor", "Thomas", "Hernandez", "Moore", "Martin", "Jackson", "Thompson", "White",
    "Lopez", "Lee", "Gonzalez", "Harris", "Clark", "Lewis", "Young", "Walker", "Hall", "Allen",
    "King", "Wright", "Scott", "Green", "Adams", "Baker", "Nelson", "Hill", "Ramirez", "Campbell",
    "Mitchell", "Roberts", "Carter", "Phillips", "Evans", "Turner", "Torres", "Parker", "Collins", "Edwards",
    "Stewart", "Flores", "Morris", "Nguyen", "Murphy", "Rivera", "Cook", "Rogers", "Morgan", "Peterson",
    "Cooper", "Reed", "Bailey", "Bell", "Gomez", "Kelly", "Howard", "Ward", "Cox", "Diaz",
    "Richardson", "Wood", "Watson", "Brooks", "Bennett", "Gray", "James", "Reyes", "Cruz", "Hughes",
    "Price", "Myers", "Long", "Foster", "Sanders", "Ross", "Morales", "Powell", "Sullivan", "Russell",
    "Ortiz", "Jenkins", "Gutierrez", "Perry", "Butler", "Barnes", "Fisher", "Henderson", "Coleman", "Simmons",
    "Patterson", "Jordan", "Reynolds", "Hamilton", "Graham", "Kim"
]

EVENT_TYPES = ['bought_insurance']
PROPERTIES = {
    'value': lambda: round(random.uniform(120, 350), 2),
}

# Counts & invalidity percentages
COUNT = config["COUNT"]
MAX_INVALID_PERCENTAGE = config["MAX_INVALID_PERCENTAGE"]
MAX_EMPTY_PERCENTAGE = config["MAX_EMPTY_PERCENTAGE"]

# Utility Functions
def generate_random_value(choices, include_empty=False, max_empty_percentage=MAX_EMPTY_PERCENTAGE):
    if include_empty and random.random() < max_empty_percentage:
        return ""
    return choices() if callable(choices) else random.choice(choices)

def generate_event_timestamp():
    if random.random() < MAX_INVALID_PERCENTAGE:
        return ""
    now = datetime.now(timezone.utc)
    random_offset = timedelta(days=random.randint(-90, 0), hours=random.randint(0, 23), minutes=random.randint(0, 59))
    event_time = now + random_offset
    return int(event_time.timestamp())

def generate_random_id():
    return str(uuid.uuid4())

def generate_data(count=COUNT, max_invalid_percentage=MAX_INVALID_PERCENTAGE, max_empty_percentage=MAX_EMPTY_PERCENTAGE, use_random_id=False):
    data = []
    for _ in range(count):
        is_invalid = random.random() < max_invalid_percentage
        
        # Generate email and hash it unless it's meant to be invalid (empty)
        email = "" if is_invalid else f"{random.choice(FIRST_NAMES)}.{random.choice(LAST_NAMES)}{random.randint(1,9999)}@gmail.com".lower()
        hashed_email = hashlib.sha256(email.encode()).hexdigest() if email else ""
        
        # Adjust generation for event types and timestamps to potentially be empty
        event_type = generate_random_value(EVENT_TYPES, include_empty=is_invalid, max_empty_percentage=max_empty_percentage)
        event_timestamp = generate_event_timestamp()
        
        # Generate properties dynamically
        row = [
            generate_random_id() if use_random_id else hashed_email,
            event_type,
            event_timestamp,
            *[generate_random_value(PROPERTIES[prop], include_empty=True, max_empty_percentage=max_empty_percentage) for prop in PROPERTIES]
        ]
        data.append(row)
    return data

# Generate and prepare data for DataFrame
columns = ["id_c6", "event_type", "event_timestamp"] + [f"prop_{prop}" for prop in PROPERTIES]
df = pd.DataFrame(generate_data(use_random_id=True), columns=columns)

# Define the subdirectory and filename
subdirectory = 'Outputs/Event Files'
current_datetime = datetime.now().strftime('%Y-%m-%d_%H%M')
count_in_k = f"{COUNT//1000}K" if COUNT >= 1000 else f"{COUNT}"
filename = f"{count_in_k}_events_{current_datetime}.csv"
filepath = os.path.join(subdirectory, filename)

# Ensure the subdirectory exists
os.makedirs(subdirectory, exist_ok=True)

# Save the DataFrame to CSV
df.to_csv(filepath, index=False)

print(f"File saved to: {filepath}")
