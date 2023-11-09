import json
import filter_data

def extract_nested_objects(data, extracted_objects):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "objects" and isinstance(value, list):
                for obj in value:
                    extracted_objects.append(obj)
            else:
                extract_nested_objects(value, extracted_objects)
    elif isinstance(data, list):
        for item in data:
            extract_nested_objects(item, extracted_objects)

# Load the JSON file
with open('full_stix_data.json', 'r') as file:
    json_data = json.load(file)

# Initialize an empty list to store the extracted objects
extracted_objects = []

# Extract nested objects
extract_nested_objects(json_data, extracted_objects)



filter_data.main(extracted_objects)

# # Specify the file path where you want to save the extracted objects
# file_path = "extracted_objects.json"

# # Open the file in write mode
# with open(file_path, "w") as file:
#     # Iterate through the extracted objects and write them to the file
#     file.write("[\n")
#     for obj in extracted_objects:
#         # Write each object to the file with proper indentation

#         file.write(json.dumps(obj, indent=4))
#         file.write(",\n")
#     file.write("]")

# # Close the file when done
# print("Extracted objects have been written to:", file_path)

# # Print the extracted objects
# for obj in extracted_objects:
#     print(json.dumps(obj, indent=4), "\n\n")

print(len(extracted_objects))
