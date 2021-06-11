from flask import Flask
from flask import request
from Model import db
import json
import statistics

DB = db.DatabaseDriver()
app = Flask(__name__)

def success_response(data, code=200):
    return json.dumps({"success":True, "data":data}),code

def failure_response(data, code=404):
    return json.dumps({"success":False, "message":data}),code

@app.route("/")
def success():
    return "Successfully connected to DB"

@app.route("/getdb/")
def getdb():
    return success_response(DB.get_all())

@app.route("/add/", methods=["POST"])
def add():
    body = json.loads(request.data)
    number = body.get("number_ppl")
    if type(number) != int:
        return failure_response("Invalid Type, Not an Integer")
    else:
        return success_response(DB.add_data(number),201)

@app.route("/delete/<int:id>/", methods=["DELETE"])
def delete(id):
    if DB.find(id) == None:
        return failure_response("Invalid id!")
    else:
        return success_response(DB.delete(id))

@app.route("/getcurrent/")
def get_current_number_of_people():
    dict_list = DB.get_most_recent(5)
    temp = []
    for row in dict_list:
        num = row.get("number_ppl")
        temp.append(num)
    median_count = {
        "median_number_of_ppl": statistics.median(temp)
    }
    return success_response(median_count)

if __name__ == "__main__":
    app.run(debug=True)