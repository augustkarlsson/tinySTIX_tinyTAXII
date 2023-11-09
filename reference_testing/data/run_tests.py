import json
import argparse
import os
from tinySTIX_generator import map_keys_and_values_to_int, to_cbor

def main(input_folder,output_folder,verbose_mode):
    files = os.listdir(input_folder)

    sizes =  {}
    for file in files:
        extracted_objects = []
        sizes[file] = {}
        reductions = []
        cbor_objects = []
        input_path = input_folder+"/"+file
        #print("Read file", input_path)
        all_mapped_data = []

        with open(input_path, "r") as objects_file:
            for line in objects_file:
                line = line.strip()
                line = json.loads(line)
                extracted_objects.append(line)

        with open("properties.json", 'r') as f:
            property_name_mapping = json.load(f)
            with open("values.json", 'r') as f:
                property_name_value_mapping = json.load(f)
                for data in extracted_objects:
                    original_size = len(str(data).encode("utf-8"))
                    mapped_data = map_keys_and_values_to_int(data, property_name_mapping, property_name_value_mapping)
                    all_mapped_data.append(mapped_data)
                    cbor = to_cbor(mapped_data)
                    #cbor = to_cbor(data)
                    cbor_objects.append(cbor)
                    cbor_size = len(cbor)
                    #print(original_size)#, cbor_size)
                    reductions.append((1-float(cbor_size)/float(original_size))*100)

        output_path = output_folder+"/"+file

        with open(output_path, "wb") as file:
            for data in cbor_objects:
                file.write(data + b'\n')
        #print("Wrote", len(cbor_objects), "objects to file", output_path)

        # non_integer_keys = set()

     
        # for data in all_mapped_data:
        #     for key in data:
        #         if not isinstance(key, int):
        #             non_integer_keys.add(key)

        # print("Keys with non-integer values:", non_integer_keys)

        # added 24th
        # sorted_objects = [str(o) for o in extracted_objects]
        # sorted_mapped_objects = [str(o) for o in all_mapped_data]

        print(file)
        sorted_objects = extracted_objects
        sorted_mapped_objects = all_mapped_data

        # zip and sort
        zipped_pairs = zip(reductions, sorted_objects)
        sorted_pairs = sorted(zipped_pairs, key=lambda x: x[0])  # Sorting based on reductions

        sorted_reductions = [x for x, _ in sorted_pairs]
        sorted_sorted_objects = [x for _, x in sorted_pairs]

        zipped_pairs2 = zip(reductions, sorted_mapped_objects)
        sorted_pairs2 = sorted(zipped_pairs2, key=lambda x: x[0])  # Sorting based on reductions

        sorted_reductions2 = [x for x, _ in sorted_pairs2]
        sorted_sorted_mapped_objects2 = [x for _, x in sorted_pairs2]

        zipped_pairs3 = zip(reductions, cbor_objects)
        sorted_pairs3 = sorted(zipped_pairs3, key=lambda x: x[0])  # Sorting based on reductions

        sorted_reductions3 = [x for x, _ in sorted_pairs3]
        sorted_sorted_mapped_objects3 = [x for _, x in sorted_pairs3]


        print("Worst reduction object:")
        print(json.dumps(sorted_objects[0], indent=3))
        print("\n\n")

        print("Worst reduction object mapped:")
        print(json.dumps(sorted_mapped_objects[0], indent=3))
        print("\n\n")

        print("Worst reduction object cbor:")
        binary_representation = ' '.join([bin(byte) for byte in cbor_objects[0]])
        print(binary_representation)
        print(len(cbor_objects[0]))
        print("\n\n")

        print("Best reduction object:")
        print(json.dumps(sorted_objects[-1], indent=3))
        print("\n\n")

        print("Best reduction object mapped:")
        print(json.dumps(sorted_mapped_objects[-1], indent=3))
        print("\n\n")

        print("Worst reduction object cbor:")
        binary_representation = ' '.join([bin(byte) for byte in cbor_objects[-1]])
        print(binary_representation)
        print(len(cbor_objects[-1]))
        print("\n\n")

        print("Worst reduction:", sorted_reductions[0], "best reduction:", sorted_reductions[-1])
        print("\n--------------------------------------------------------------\n")

        # print("Worst reduction object:")
        # print(json.dumps(sorted_sorted_objects[0], indent=3))
        # print("\n\n")
        # print("Worst reduction object mapped:", json.dumps(sorted_sorted_mapped_objects2[0]), "\n\n")

        # print("best reduction object:", json.dumps(sorted_sorted_objects[-1]), "\n\n")
        # print("best reduction object mapped:", json.dumps(sorted_sorted_mapped_objects2[-1]), "\n\n")
        # print("Worst reduction:", sorted_reductions[0], "best reduction:", sorted_reductions[-1])
        # print("\n--------------------------------------------------------------\n")







        # #print(type(extracted_objects))
        # sorted_objects = []
        # for o in extracted_objects:
        #     sorted_objects.append(str(o))
        # #print(extracted_objects)
        # zipped_pairs = zip(reductions, sorted_objects)
 
        # # z = [x for _, x in sorted(zipped_pairs)]
        # # y = [x for x, _ in sorted(zipped_pairs)]
        # # print("Worst reduction object:",z[0], "best reduction object:", z[-1])
        # # print("reduction ", y[0], "best", y[-1])
        # reductions.sort()
        # mean = float(sum(reductions))/float(len(reductions))
        # #print("Average size reduction over {:d} objects: {:.2f}%".format(len(reductions),mean))
        # #print("Smallest reduction: {:.2f}% and greatest reduction: {:.2f}%\n\n".format(reductions[0], reductions[-1]))
              
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script for parsing CTI in STIX format")
    parser.add_argument("input_folder", help="Path to the input folder")
    parser.add_argument("output_folder", help="Path to the output folder")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode, display omitted key-value pairs")
    
    args = parser.parse_args()

    input_folder = args.input_folder
    output_folder = args.output_folder
    verbose_mode = args.verbose

    main(input_folder,output_folder,verbose_mode)

    