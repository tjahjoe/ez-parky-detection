from gate import gate
from detection import detection
from threading import Thread
from flask import Flask, jsonify, request

app = Flask(__name__)
data = {'data' : 'False'}

@app.route('/openGate', methods=['POST'])
def post_open_gate():
    global data
    data = request.json
    return data

@app.route('/gate', methods=['GET'])
def get_open_gate():
    global data
    return jsonify(data)


if __name__ == "__main__":
    program_one = Thread(target=detection)
    program_two = Thread(target=gate)
    
    program_one.start()
    program_two.start()
    app.run(host='0.0.0.0')
    
    program_one.join()
    program_two.join()
    