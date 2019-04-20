from flask import Flask, request
import flask
import json
app = Flask(__name__)


@app.route('/')
def home():
    return "Connected To Server"



@app.route('/loginInfo', methods=["POST"])
def query():
    data = request.get_data()
    data = data.decode("utf-8")
    print("data received .. ", data)
    q_res = {"res": "success"}
    res = flask.make_response(flask.jsonify(q_res))
    return res




def formHeader(res):
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'POST'
    res.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return res


if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True, port = '8080')
