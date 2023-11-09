import json
import argparse
import os

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

# Function to filter out key-value pairs with unusually large values
def filter_large_values(data, threshold_length, filtered_out: list):
    for item in data:
        filtered_item = {}
        for key, value in item.items():
            if isinstance(value, str) and len(value) <= threshold_length:
                filtered_item[key] = value
            elif isinstance(value, (list, dict)) and len(str(value).encode("utf-8")) <= threshold_length:
                filtered_item[key] = value
            elif not isinstance(value, (str, list, dict)):
                filtered_item[key] = value
            else:
                filtered_out.append({key: value})  # Store filtered out key-value pairs
        yield filtered_item

def main(input_folder, output_folder, verbose_mode, threshold_option):
    files = os.listdir(input_folder)

    # Print the list of files
    for file in files:

        # Initialize an empty list to store the extracted objects
        extracted_objects = []
        filtered_out = []

        input_path = input_folder+"/"+file
        print("Read file", input_path)
        if verbose_mode:
            print("__________________________________________________________________")
        with open(input_path, "r") as stix_file:
            json_data = json.load(stix_file)
            extract_nested_objects(json_data, extracted_objects)
           
            filtered_data = list(filter_large_values(extracted_objects, threshold_option, filtered_out))

            if verbose_mode:
                print("Kept the following data:")
                
            #Otherwise the data is written with single quotes ' as is default in Python. 
            #Data cannot be parsed with json loads if not double quotes.
            for i in range(0,len(filtered_data)):
                filtered_data[i] = json.dumps(filtered_data[i])
                if verbose_mode:
                    print(i+1,':', filtered_data[i], "\n")

            if verbose_mode:  
                print("Filtered out the following", len(filtered_out), "keys with corresponding values:\n")
                for out in filtered_out:
                    print("\t",out, "\n")
                print("__________________________________________________________________")

        output_path = output_folder+"/"+file.split('.')[0]+".txt"
        print("Wrote", len(filtered_data), "objects to file", output_path)
        with open(output_path, "w") as list_file:
            for data in filtered_data:
                list_file.write(str(data))
                list_file.write("\n")

        print("==================================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script for parsing CTI in STIX format")
    parser.add_argument("input_folder", help="Path to the input folder")
    parser.add_argument("output_folder", help="Path to the output folder")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode, display omitted key-value pairs")
    parser.add_argument("-t", "--threshold", type=int, default=100, help="Set threshold of which data larger than will be filtered out")
    
    args = parser.parse_args()

    input_folder = args.input_folder
    output_folder = args.output_folder
    verbose_mode = args.verbose
    threshold_option = args.threshold

    main(input_folder,output_folder,verbose_mode,threshold_option)

    