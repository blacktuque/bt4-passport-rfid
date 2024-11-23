import yaml
import nfc.clf
import logging
import passport
import yaml
import math

from nfc.clf import RemoteTarget
from nfc.tag.tt2 import Type2Tag

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger("nfc.clf").setLevel(logging.DEBUG)
logging.getLogger("nfc.dep").setLevel(logging.DEBUG)

def load_yaml(file_path):
    """Load the YAML file."""
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        return data
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None

def display_menu(data, num_columns=3):
    """Display the menu in columns with correct numbering."""
    menu_items = list(data.keys())
    num_rows = math.ceil(len(menu_items) / num_columns)
    
    # Create rows of items for column display
    rows = []
    for i in range(num_rows):
        row = menu_items[i * num_columns : (i + 1) * num_columns]
        rows.append(row)
    
    print("Menu:")
    for row_idx, row in enumerate(rows):
        line = []
        for col_idx, item in enumerate(row):
            item_number = row_idx * num_columns + col_idx + 1
            line.append(f"{item_number}. {item}".ljust(30))  # Adjust padding for alignment
        print("  ".join(line))
    print()

def get_selection(data):
    """Prompt the user to select an item from the menu."""
    while True:
        try:
            choice = int(input("Enter the number of your selection: "))
            if 1 <= choice <= len(data):
                selected_key = list(data.keys())[choice - 1]
                return selected_key, data[selected_key]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def validate_input(prompt, expected_type, default):
    """Validate user input based on the expected type and handle defaults."""
    while True:
        user_input = input(prompt).strip()
        if not user_input:  # Use default value if input is empty
            return default
        try:
            if expected_type == "integer":
                return int(user_input)
            elif expected_type == "float":
                return float(user_input)
            elif expected_type == "boolean":
                # Convert common boolean strings to boolean values
                if user_input.lower() in ["true", "yes", "y", "1"]:
                    return True
                elif user_input.lower() in ["false", "no", "n", "0"]:
                    return False
                else:
                    raise ValueError("Invalid boolean value.")
            elif expected_type == "string":
                return user_input
            else:
                print(f"Unsupported type: {expected_type}.")
                return user_input
        except ValueError:
            print(f"Invalid input. Please provide a value of type {expected_type}.")

def populate_suboptions(suboptions):
    """Prompt the user to populate values for each sub-option."""
    populated = {}
    print("\nEnter values for the following fields:")
    for suboption in suboptions:
        # Suboptions are dictionaries with {field_name: {type: ..., default: ...}}
        for field, attributes in suboption.items():
            field_type = attributes.get("type", "string")
            default_value = attributes.get("default", None)
            prompt = f"  {field} ({field_type}, default: {default_value}): "
            value = validate_input(prompt, field_type, default_value)
            populated[field] = value
    return populated

if __name__ == "__main__":
    while True:
        # Specify your YAML file path
        yaml_file = 'all_items.yml'

        # Load YAML data
        data = load_yaml(yaml_file)

        # Display menu and get user selection
        display_menu(data)
        selected_key, selected_value = get_selection(data)

        # Populate sub-options if available
        if isinstance(selected_value, list):
            populated_values = populate_suboptions(selected_value)
            selected_item = {selected_key: populated_values}
        else:
            selected_item = {selected_key: selected_value}

        item_yml = yaml.dump(selected_item, default_flow_style=False)

        print("\nYou selected:")
        print(item_yml)

        input("Press to Write Item")

        with nfc.clf.ContactlessFrontend() as r:
            try:
                r.open('tty:ACM0:pn532')
            except:
                r.open('tty:ACM1:pn532')

            sense_res = r.sense(RemoteTarget("106A"))

            if sense_res:
                print(f"Found: {sense_res}")
                tag = Type2Tag(r, sense_res)

                print(f"id: {tag.identifier}")
                tag.write(4, b"\x00\x00\x00\x00")

                b = passport.create_item_tag_from_yaml(tag.identifier, item_yml)
                
                print(f"data:{b}")
                for i in range(25):
                    tag.write(0x20+i, b[i*4:i*4+4])
                print(item_yml)
