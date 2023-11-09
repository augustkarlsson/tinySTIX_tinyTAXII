from flask import Flask, request, jsonify
import argparse

app = Flask(__name__)

data_list = []

# Initialize the resource index
current_resource_index = 0

@app.route('/access_resource', methods=['GET'])
def access_resource():
    global current_resource_index
    
    if current_resource_index < len(data_list):
        # Allocate the current resource
        resource = data_list[current_resource_index]
        current_resource_index += 1
        return resource
    else:
        return {'error': 'No more resources available'}, 404

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Populate server with list of tinySTIX messages")
    parser.add_argument('-f', '--file', required=True, help='Path to the file with IoCs.')
    args = parser.parse_args()
    file = args.file

    #with open("cbor_list.txt", "rb") as file:
    with open(file, "rb") as file:
        while True:
            # Read a line (up to the delimiter) and break if the end of file is reached
            line = file.readline()
            if not line:
                break
            # Append the byte-string to the list
            data_list.append(line.strip())  

    #remove ssl_context if HTTP
    app.run(debug=True, host='::1', port=9002, ssl_context=('cert.pem', 'key.pem'))