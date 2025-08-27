project/
│── app.py
│── routes/
│    ├── users.py
│    ├── todos.py
│── models/
│    ├── user.py
│    ├── todo.py




``` App Setup and Configurations, 


mkdir dailydev-backend
cd dailydev-backend
2️⃣ Create a Virtual Environment (Recommended)
This keeps your project’s dependencies isolated.

bash
Copy
Edit
python3 -m venv venv
Activate it:

bash
Copy
Edit
source venv/bin/activate
Your terminal should now show (venv) at the start of the prompt.

3️⃣ Install Flask and Other Dependencies
Inside the activated environment:

bash
Copy
Edit
pip install flask flask-cors flask-pymongo
flask → The web framework.

flask-cors → Allows your HTML frontend to call the backend.

flask-pymongo → Lets Flask talk to MongoDB.

4️⃣ Create Your Flask App
Create a file named app.py:

bash
Copy
Edit
touch app.py
Paste in the backend code I gave you earlier (with MongoDB connection settings updated for your system).

5️⃣ Set Environment Variables
On macOS:

bash
Copy
Edit
export FLASK_APP=app.py
export FLASK_ENV=development
(FLASK_ENV=development enables hot reload and debug mode.)

6️⃣ Run the Application
bash
Copy
Edit
flask run
You should see something like:

csharp
Copy
Edit
 * Running on http://127.0.0.1:5000
7️⃣ Test It
Open another terminal and test with:

bash
Copy
Edit
curl http://127.0.0.1:5000/todos
Or just visit the URL in your browser.

If you want, I can now adjust the MongoDB connection part of the Flask code so it connects directly to your local MongoDB or Atlas cloud database — otherwise Flask will run but won’t store data yet.

Do you want me to configure that next?