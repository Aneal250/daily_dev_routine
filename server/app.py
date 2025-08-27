import os
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_cors import CORS
from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
import uuid
from dotenv import load_dotenv

load_dotenv() 

app = Flask(__name__)
CORS(app)

# --- Configuration ---
# Load config from environment variables for better security
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/dailydev")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "a_default_fallback_secret_key")
mongo = PyMongo(app)

# --- Authentication Helper ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Authentication token is missing!"}), 401

        try:
            # Expecting "Bearer <token>"
            token = token.split(" ")[1]
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = mongo.db.users.find_one({"_id": ObjectId(data["user_id"])})
            if not current_user:
                return jsonify({"message": "Invalid token user!"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except (jwt.InvalidTokenError, IndexError):
            return jsonify({"message": "Invalid token!"}), 401
        except Exception as e:
            return jsonify({"message": "An unknown error occurred", "error": str(e)}), 500
            
        return f(current_user, *args, **kwargs)
    return decorated

# --- User Routes ---
@app.route("/register", methods=["POST"])
def register_user():
    data = request.json
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Email and password are required"}), 400

    if mongo.db.users.find_one({"email": data["email"].lower()}):
        return jsonify({"message": "A user with this email already exists"}), 409 # 409 Conflict is more specific

    # Use Werkzeug's default, secure hashing method (includes salt)
    hashed_pw = generate_password_hash(data["password"])
    
    user_id = mongo.db.users.insert_one({
        "email": data["email"].lower(),
        "firstName": data.get("firstName", ""),
        "lastName": data.get("lastName", ""),
        "password": hashed_pw,
        "createdAt": datetime.utcnow()
    }).inserted_id

    return jsonify({"message": "User registered successfully", "userId": str(user_id)}), 201

@app.route("/login", methods=["POST"])
def login_user():
    data = request.json
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Email and password are required"}), 400

    user = mongo.db.users.find_one({"email": data["email"].lower()})

    if not user or not check_password_hash(user["password"], data["password"]):
        return jsonify({"message": "Invalid email or password"}), 401

    token = jwt.encode({
        "user_id": str(user["_id"]),
        "exp": datetime.utcnow() + timedelta(hours=24)
    }, app.config["SECRET_KEY"], algorithm="HS256")

    return jsonify({"token": token})

@app.route("/profile", methods=["GET"])
@token_required
def get_profile(current_user):
    # Create a profile endpoint for the logged-in user
    profile_data = {
        "_id": str(current_user["_id"]),
        "email": current_user["email"],
        "firstName": current_user.get("firstName"),
        "lastName": current_user.get("lastName"),
    }
    return jsonify(profile_data)

# --- Todo Routes ---
@app.route("/todos", methods=["GET", "POST"])
@token_required
def handle_todos(current_user):
    user_id_str = str(current_user["_id"])

    if request.method == "POST":
        data = request.json
        todo_date = data.get("date", date.today().isoformat())
        
        todos_with_ids = []
        for t in data.get("todos", []):
            todos_with_ids.append({
                "id": t.get("id", str(uuid.uuid4())), # Ensure ID exists
                "todo": t.get("todo", ""),
                "description": t.get("description", ""),
                "isChecked": t.get("isChecked", False)
            })

        mongo.db.dailyTodos.update_one(
            {"userId": user_id_str, "date": todo_date},
            {"$set": {"todos": todos_with_ids}},
            upsert=True
        )
        return jsonify({"message": "Todos saved successfully"}), 201

    if request.method == "GET":
        todo_date = request.args.get("date", date.today().isoformat())
        todos_doc = mongo.db.dailyTodos.find_one(
            {"userId": user_id_str, "date": todo_date}
        )
        
        if not todos_doc:
            return jsonify({"date": todo_date, "todos": []}) # Return empty list if no doc
        
        todos_doc["_id"] = str(todos_doc["_id"])
        return jsonify(todos_doc)


@app.route("/todos/mark", methods=["PATCH"])
@token_required
def mark_todo(current_user):
    data = request.json
    try:
        todo_date = data["date"]
        todo_id = data["todoId"]
        is_checked = data["isChecked"]
    except KeyError:
        return jsonify({"message": "Missing required fields: date, todoId, isChecked"}), 400

    result = mongo.db.dailyTodos.update_one(
        {"userId": str(current_user["_id"]), "date": todo_date, "todos.id": todo_id},
        {"$set": {"todos.$.isChecked": is_checked}}
    )
    if result.modified_count == 0:
        return jsonify({"message": "Todo not found or already has the same status"}), 404
        
    return jsonify({"message": "Todo status updated successfully"}), 200

@app.route("/todos/<string:todo_id>", methods=["DELETE"])
@token_required
def delete_todo(current_user, todo_id):
    todo_date = request.args.get("date")
    if not todo_date:
        return jsonify({"message": "The 'date' query parameter is required"}), 400

    result = mongo.db.dailyTodos.update_one(
        {"userId": str(current_user["_id"]), "date": todo_date},
        {"$pull": {"todos": {"id": todo_id}}}
    )
    if result.modified_count == 0:
        return jsonify({"message": "Todo not found for the specified date"}), 404
        
    return jsonify({"message": "Todo deleted successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)