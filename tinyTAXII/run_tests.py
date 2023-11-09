import json

import split_data
import filter_data
import sys
sys.path.append('../tinySTIX')
import tinySTIX_generator


def main(path = 'full_stix_data.json'):
    # Load the JSON file
    with open(path, 'r') as file:
        json_data = json.load(file)

    # Initialize an empty list to store the extracted objects
    extracted_objects = []

    # Extract nested objects
    split_data.extract_nested_objects(json_data, extracted_objects)

    extracted_objects = filter_data.main(extracted_objects)
    
    all_cbor = []
    reductions = []
    for stix in extracted_objects:
        data, reduction = tinySTIX_generator.main("../tinySTIX/properties.json", "../tinySTIX/values.json", False, stix, False)
        all_cbor.append(data)
        reductions.append(float(reduction))
        print(data)
    
    print("Average is size reduction over {} STIX objects is {:.2f}%.".format(len(all_cbor),sum(reductions)/len(reductions)))

    with open("cbor_list.txt", "wb") as file:
        for cbor in all_cbor:
            file.write(cbor + b'\n')



    print(len(list_objects))
    print(list_objects)
            
if __name__ == "__main__":
    main()
