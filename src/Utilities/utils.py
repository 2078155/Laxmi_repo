import uuid
from datetime import datetime
import re



def get_current_time():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    return formatted_time


def calculate_time_difference(current_time: str):
    datetime_obj1 = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')

    # Get the current datetime
    current_datetime = datetime.now()

    # Calculate the difference
    time_difference = current_datetime - datetime_obj1
    # Convert the time difference to minutes
    minutes_difference = time_difference.total_seconds() / 60

    return minutes_difference


def release_file_pattern_check(file_name: str):
    pattern = r"Release (\d+\.\d+\.\d+) - ([A-Za-z]+ \d+(?:st|nd|rd|th), \d{4})\.md"

    # Use re.match to check if the string matches the pattern
    match = re.match(pattern, file_name)

    if match:
        release_version = match.group(1)
        release_date = match.group(2)

        return True, release_version, release_date
    else:
        return False, None, None


def filter_duplicate_file_names(list_of_files):
    # Create a set to keep track of unique file_name values
    unique_names = set()
    # Create a new list to store the items with unique file_name values
    filtered_data = []
    for item in list_of_files:
        file_name = item["file_name"]
        if file_name not in unique_names:
            unique_names.add(file_name)
            filtered_data.append(item)
    return filtered_data


def unique_id_generator():
    """
    Generate a unique ID using UUID version 4.
    """
    return str(uuid.uuid4())



