import cbor2
import json
import argparse
from pathlib import Path    

def map_keys_to_str(data, keyword_conversion_table):
    if isinstance(data, dict):
        new_dict = {}
        for k, v in data.items():
            str_key = next((key for key, value in keyword_conversion_table.items() if value == k), k)
            new_dict[str_key] = map_keys_to_str(v, keyword_conversion_table)
        return new_dict
    elif isinstance(data, list):
        return [map_keys_to_str(item, keyword_conversion_table) for item in data]
    else:
        return data
    
def map_values_to_str(data, property_name_value_mapping):
    if isinstance(data, dict):
        new_dict = {}
        for k, value in data.items():
            if isinstance(value, int) and k in property_name_value_mapping:
                for key, val in property_name_value_mapping[k].items():
                    if value == val:
                        new_dict[k] = key 
            else:
                new_dict[k] = map_values_to_str(value, property_name_value_mapping)
        return new_dict
    elif isinstance(data, list):
        return [map_values_to_str(item, property_name_value_mapping) for item in data]
    else:
        return data

def map_keys_and_values_to_int(data, keyword_conversion_table, property_name_value_mapping):
    if isinstance(data, dict):
        new_dict = {}
        for k, v in data.items():
            if k in keyword_conversion_table:
                new_key = keyword_conversion_table[k]
                if isinstance(v, dict):
                    new_dict[new_key] = map_keys_and_values_to_int(v, keyword_conversion_table, property_name_value_mapping)
                elif isinstance(v, list):
                    new_dict[new_key] = [map_keys_and_values_to_int(item, keyword_conversion_table, property_name_value_mapping) for item in v]
                elif k in property_name_value_mapping:
                    new_dict[new_key] = property_name_value_mapping[k].get(v, v)
                else:
                    new_dict[new_key] = v
            else:
                new_dict[k] = map_keys_and_values_to_int(v, keyword_conversion_table, property_name_value_mapping)
        return new_dict
    elif isinstance(data, list):
        return [map_keys_and_values_to_int(item, keyword_conversion_table, property_name_value_mapping) for item in data]
    else:
        return data

def print_data_with_indent(data, indent=0):
    if isinstance(data, dict):
        for k, v in data.items():
            print(" " * indent + str(k) + ":")
            print_data_with_indent(v, indent + 4)
    elif isinstance(data, list):
        for item in data:
            print_data_with_indent(item, indent + 4)
    else:
        print(" " * indent + str(data))

def to_cbor(data):
    return cbor2.dumps(data)

def from_cbor(data):
    return cbor2.loads(data)


def main(properties="properties.json", values="values.json", data_as_file=True, data="stix_data.json", print_data=True, debug=False):
    with open(properties, 'r') as f:
        property_name_mapping = json.load(f)
        with open(values, 'r') as f:
            property_name_value_mapping = json.load(f)

            if data_as_file:
                stix_data = ""
                with open(data, "r") as f:
                    stix_data = json.load(f)
            else:
                stix_data = data

            
            # Measure the size of the original STIX data
            original_size = len(str(stix_data).encode('utf-8'))

            if debug:
                #Original data
                print(json.dumps(stix_data, indent=4))
            if print_data:
                print(f"Original size: {original_size} bytes")


            # Encode the STIX data using CBOR
            cbor_data = cbor2.dumps(stix_data)

            # Measure the size of the CBOR-encoded data
            cbor_size = len(cbor_data)
            #print(f"CBOR Size: {cbor_size} bytes")

            mapped_data = map_keys_and_values_to_int(stix_data, property_name_mapping, property_name_value_mapping)
            #mapped_size = len(str(mapped_data).encode('utf-8'))
            #print(f"Mapped Size: {mapped_size} bytes")
            if debug:
                print(mapped_data, "\n\n")

            # # Convert to CBOR format
            cbor_data = cbor2.dumps(mapped_data)
            # # Measure the size of the CBOR-encoded data
            cbor_size = len(cbor_data)


            if debug:
                print(cbor_data)
            if print_data:
                print(f"Converted size after integer conversion and CBOR: {cbor_size} bytes")

            mapped_data = cbor2.loads(cbor_data)
            unmapped_data = map_keys_to_str(mapped_data, property_name_mapping)
            #print("Keys reverted",json.dumps(unmapped_data, indent=4))
            unmapped_data = map_values_to_str(unmapped_data, property_name_value_mapping)
            #print("Values reverted",json.dumps(unmapped_data, indent=4))

            # Measure the size of the original and reverted STIX data
            reverted_size = len(str(unmapped_data).encode('utf-8'))

            if debug:
                print(f"Reverted Size: {reverted_size} bytes")
                print(f"Original Size: {original_size} bytes")
            reduction = (1-float(cbor_size)/float(original_size))*100
            if print_data:
                print("Size reduction: {:.2f}%\n\n".format(reduction))

            return (cbor_data, reduction)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert STIX <-> tinySTIX")
    parser.add_argument('-ft',"--feature", choices={"export", "import"}, help="Main feature: {export,import} \n\n" +
    'export: Export STIX to tinySTIX' +
   ' import: Import tinySTIX to STIX')
    parser.add_argument('-f', '--file', nargs='+', type=Path, required=True, help='Path to the file(s) to convert.')
    parser.add_argument('-s', '--single_output', action='store_true',help='Produce only one result file (in case of multiple input file).')
    parser.add_argument('-od','--output_dir', type=Path,help='Output path - used in the case of multiple input files when the `single_output` argument is not used.')
    parser.add_argument('-o', '--output_name', type=Path, help='Output file name - used in the case of a single input')
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode")
    parser.add_argument('--values_mapping', default="values.json",type=Path, help='Path to the json file for values mapping.')
    parser.add_argument('--keywords_mapping', default="properties.json",type=Path, help='Path to the json file for keywords mapping.')

    
    args = parser.parse_args()

    feature = args.feature
    file = args.file
    single_output = args.single_output
    output_dir = args.output_dir
    output_name = args.output_name
    verbose_mode = args.verbose
    values_mapping = args.values_mapping
    keywords_mapping = args.keywords_mapping
    print(verbose_mode)
    #main(values_mapping, keywords_mapping, True, file, verbose_mode)