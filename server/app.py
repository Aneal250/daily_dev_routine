from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_cors import CORS
from datetime import date

app = Flask(__name__)
CORS(app)

# MongoDB Config
app.config["MONGO_URI"] = "mongodb://localhost:27017/dailydev"
mongo = PyMongo(app)

# -------- USERS --------
@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    user_id = mongo.db.users.insert_one({
        "email": data["email"],
        "firstName": data["firstName"],
        "lastName": data["lastName"]
    }).inserted_id
    return jsonify({"userId": str(user_id)}), 201

@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    user["_id"] = str(user["_id"])
    return jsonify(user)

# -------- TODOS --------
@app.route("/todos", methods=["POST"])
def create_or_update_todos():
    data = request.json
    user_id = data["userId"]
    todo_date = data.get("date", date.today().isoformat())

    mongo.db.dailyTodos.update_one(
        {"userId": user_id, "date": todo_date},
        {"$set": {
            "userId": user_id,
            "date": todo_date,
            "todos": data["todos"]
        }},
        upsert=True
    )
    return jsonify({"message": "Todos saved successfully"}), 201

@app.route("/todos", methods=["GET"])
def get_todos():
    user_id = request.args.get("userId")
    todo_date = request.args.get("date", date.today().isoformat())
    todos_doc = mongo.db.dailyTodos.find_one({"userId": user_id, "date": todo_date})
    if not todos_doc:
        return jsonify({"todos": []})
    todos_doc["_id"] = str(todos_doc["_id"])
    return jsonify(todos_doc)

@app.route("/todos/mark", methods=["PATCH"])
def mark_todo():
    data = request.json
    user_id = data["userId"]
    todo_date = data["date"]
    todo_id = data["todoId"]
    completed = data["completed"]

    mongo.db.dailyTodos.update_one(
        {"userId": user_id, "date": todo_date, "todos.id": todo_id},
        {"$set": {"todos.$.completed": completed}}
    )
    return jsonify({"message": "Todo updated"}), 200

if __name__ == "__main__":
    app.run(debug=True)
