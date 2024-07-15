import csv
import json
import re
from datetime import datetime

def sanitize_event_type(event_type):
    # Replace underscores and other invalid characters with hyphens and ensure it starts with a letter
    sanitized = re.sub(r'[^a-z0-9-]', '-', event_type.lower())
    if not re.match(r'^[a-z]', sanitized):
        sanitized = f'evt-{sanitized}'
    return sanitized

def generate_cli_commands_from_csv(file_path):
    event_types = {}

    # Read the CSV data from the file
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if event_type := row['event_type'].strip():
                if event_type not in event_types:
                    event_types[event_type] = set()

                for header in reader.fieldnames:
                    if header.startswith('prop_'):
                        event_types[event_type].add(header[5:])

    # Generate CLI commands for each event type
    commands = []
    for event_type, properties in event_types.items():
        schema = [
            {"bigquery_column_name": prop, "name": prop, "type": {"kind": "string"}} 
            for prop in properties
        ]
        schema_json = json.dumps(schema)
        # Sanitize the event_type to use as the event_schema_id
        sanitized_event_type = sanitize_event_type(event_type)
        cli_command = f'./optable-cli --timeout=10s event-schema create "{sanitized_event_type}" "{event_type}" "{event_type}" \'{schema_json}\''
        commands.append(cli_command)

    # Write the commands to a file
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = f'eventschema{timestamp}.txt'
    with open(output_file, 'w') as f:
        for command in commands:
            f.write(command + "\n")

    print(f"CLI commands written to {output_file}")

# MODIFY THE PATH TO SELECT WHICH EVENT FILE TO USE...
if __name__ == "__main__":
    file_path = 'Outputs/Event Files/5K_events_2024-02-02_1248.csv'
    generate_cli_commands_from_csv(file_path)
