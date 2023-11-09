import json

# Function to filter out key-value pairs with unusually large values
def filter_large_values(data, filtered_out: list):

    threshold_length = 100  # Threshold for lists or dictionaries
    threshold_string = 100  # Threshold for strings

    for item in data:
        filtered_item = {}
        for key, value in item.items():
            if isinstance(value, str) and len(value) <= threshold_string:
                filtered_item[key] = value
            elif isinstance(value, (list, dict)) and len(str(value).encode("utf-8")) <= threshold_length:
                filtered_item[key] = value
            elif not isinstance(value, (str, list, dict)):
                filtered_item[key] = value
            else:
                filtered_out.append({key: value})  # Store filtered out key-value pairs
        yield filtered_item

def main(data):
    filtered_out = []
    filtered_data = list(filter_large_values(data, filtered_out))

  
    
    # with open("filtered_stix_objects.txt", "w") as file:
    #     json.dump(filtered_data, file)

    return filtered_data
