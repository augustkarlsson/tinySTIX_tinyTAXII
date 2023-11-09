from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/send-message', methods=['GET'])
def send_message():
    data = {}
    with open("stix_data.json") as f:
        data["message"] = f.read()
    return data, 200

if __name__ == '__main__':
    app.run(debug=True, host='0000:0000:0000:0000:0000:0000:0000:0001', port=9000)