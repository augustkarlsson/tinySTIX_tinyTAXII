import argparse

def read_lines_from_file(filename):
    with open(filename, "rb") as file:
        return file.readlines()

def split_bytestring(bytestring, length=124):
    return [bytestring[i:i+length] for i in range(0, len(bytestring), length)]

def format_data(data, line_num, part_num):
    # Convert bytestring to individual bytes and format them with "0x" prefix
    byte_sequence = ', '.join([f"0x{byte:02x}" for byte in bytes.fromhex(data)])

    # Format the output string using the given line and part numbers
    formatted_string = f"static uint8_t ioc_{line_num}_{part_num}[{len(data) // 2}] = {{\n    {byte_sequence}\n}};"

    return formatted_string


def generate_data_array(all_data_names):
    entries = []
    for name in all_data_names:
        entry = f"    {{{name}, sizeof({name})}},"
        entries.append(entry)
    
    return "BinaryData dataListIoC[] = {\n" + "\n".join(entries) + "\n};"

def process_file(filename):
    lines = read_lines_from_file(filename)
    
    all_results = []
    all_data_names = [] # List to store all generated data names
    for line_num, line in enumerate(lines, start=1): # enumerate starts at 1 for line numbers
        # Convert the line to a hexadecimal string
        hex_obj = line.hex()

        chunks = split_bytestring(hex_obj)
        result = []
        for part_num, chunk in enumerate(chunks, start=1): # enumerate starts at 1 for part numbers
            result.append(format_data(chunk, line_num, part_num))
            all_data_names.append(f"ioc_{line_num}_{part_num}") # Store the generated data name

        all_results.append('\n\n'.join(result))

    # Generate the BinaryData dataListIoC array after processing all lines
    all_results.append(generate_data_array(all_data_names))

    return '\n\n'.join(all_results)





# def process_file(filename):
#     lines = read_lines_from_file(filename)
    
#     all_results = []
#     for line_num, line in enumerate(lines, start=1): # enumerate starts at 1 for line numbers
#         # Convert the line to a hexadecimal string
#         hex_obj = line.hex()

#         chunks = split_bytestring(hex_obj)
#         result = []
#         for part_num, chunk in enumerate(chunks, start=1): # enumerate starts at 1 for part numbers
#             result.append(format_data(chunk, line_num, part_num))

#         all_results.append('\n\n'.join(result))

#     return '\n\n'.join(all_results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a file with bytestrings and generate formatted data.")
    parser.add_argument("input_file", type=str, help="The input file containing bytestrings.")
    parser.add_argument("-o", "--output_file", type=str, help="The output file to save the formatted data. If not provided, the data is printed to stdout.")

    args = parser.parse_args()

    output_data = process_file(args.input_file)

    if args.output_file:
        with open(args.output_file, 'w') as f:
            f.write(output_data)
    else:
        print(output_data)
