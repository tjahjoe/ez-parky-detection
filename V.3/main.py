from gate import gate
from detection5 import load_model_and_prepare
from threading import Thread
from flask import Flask, jsonify, request

app = Flask(__name__)
data = {'data' : 'False'}
amount = {'amount' : 0}
space = [False for _ in range(8)]

@app.route('/openGate', methods=['POST'])
def post_open_gate():
    global data
    data = request.json
    return data

@app.route('/gate', methods=['GET'])
def get_open_gate():
    global data
    return jsonify(data)

@app.route('/parking', methods=['POST'])
def post_parking():
    global space
    data = request.json
    index = data.get('index')
    
    try:
        space[int(index)] = True
    except:
        pass
    
    return space

@app.route('/getParking', methods=['GET'])
def get_parking():
    global space
    return jsonify(space)

@app.route('/postAmount', methods=['POST'])
def post_amount():
    global amount
    amount = request.json
    return amount

@app.route('/getAmount', methods=['GET'])
def get_amount():
    global amount
    return jsonify(amount)

if __name__ == "__main__":
    program_one = Thread(target=load_model_and_prepare)
    program_two = Thread(target=gate)
    
    program_one.start()
    program_two.start()
    app.run(host='0.0.0.0')
    
    program_one.join()
    program_two.join()
    
