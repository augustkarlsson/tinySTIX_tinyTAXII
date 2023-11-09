import argparse
import os

def count_bytes_in_each_line(input_file, output_file=None):
    with open(input_file, 'rb') as infile:
        # Read lines (each CBOR object followed by a newline) and compute their lengths
        byte_counts = [len(line) for line in infile]

    i = 1
    for count in byte_counts:
        print(count)
        i += 1

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for count in byte_counts:
                outfile.write(f"{count}\n")

def process_directory(input_dir, output_dir=None):
    # List all files in the directory
    files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]

    for file in files:
        #print(f"Processing file: {file}")
        input_file_path = os.path.join(input_dir, file)
        
        if output_dir:
            output_file_path = os.path.join(output_dir, file + ".byte_counts.txt")
        else:
            output_file_path = None

        count_bytes_in_each_line(input_file_path, output_file_path)

def main():
    parser = argparse.ArgumentParser(description="Count the number of bytes in each line of binary files in a directory.")
    parser.add_argument("input_dir", type=str, help="Path to the input directory containing binary files")
    parser.add_argument("-o", "--output_dir", type=str, default=None, help="Path to the output directory. If not specified, results will only be printed to stdout. If specified, for each input file a corresponding output file with '.byte_counts.txt' extension will be created in this directory.")

    args = parser.parse_args()

    process_directory(args.input_dir, args.output_dir)

if __name__ == "__main__":
    main()
