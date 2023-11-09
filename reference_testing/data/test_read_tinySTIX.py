import argparse
from tinySTIX_generator import from_cbor, map_values_to_str, map_keys_to_str
from pathlib import Path
import json
def main(file):
    with open("properties.json", 'r') as f:
            property_name_mapping = json.load(f)
            with open("values.json", 'r') as f:
                property_name_value_mapping = json.load(f)
                with open(file, "rb") as f:
                    #while data = f.readline():
                    lines = f.readlines()
                    for data in lines:
                        print(data)
                        data = from_cbor(data)
                        print(data)
                        data = map_keys_to_str(data, property_name_mapping)
                        data = map_values_to_str(data, property_name_value_mapping)
                        print(data)
                        print("\n\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read a tinySTIX file")
    parser.add_argument('-f', '--file', required=True, help='Path to the file(s) to convert.')
    args = parser.parse_args()
    file = args.file


    main(file)