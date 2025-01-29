from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Database setup
DATABASE = "tasks.db"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed BOOLEAN NOT NULL DEFAULT 0
            )
        """)
        conn.commit()

init_db()  # Initialize the database

# Function to execute database queries
def query_db(query, args=(), one=False):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        result = cursor.fetchall()
        conn.commit()
        return (result[0] if result else None) if one else result

# Route to get all tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = query_db("SELECT * FROM tasks")
    return jsonify([{"id": row[0], "title": row[1], "description": row[2], "completed": bool(row[3])} for row in tasks])

# Route to get a specific task
@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = query_db("SELECT * FROM tasks WHERE id = ?", (task_id,), one=True)
    if task:
        return jsonify({"id": task[0], "title": task[1], "description": task[2], "completed": bool(task[3])})
    return jsonify({"error": "Task not found"}), 404

# Route to add a new task
@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    if "title" not in data:
        return jsonify({"error": "Title is required"}), 400
    
    query_db("INSERT INTO tasks (title, description) VALUES (?, ?)", (data["title"], data.get("description", "")))
    return jsonify({"message": "Task added successfully"}), 201

# Route to update a task
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    task = query_db("SELECT * FROM tasks WHERE id = ?", (task_id,), one=True)
    
    if not task:
        return jsonify({"error": "Task not found"}), 404

    query_db("UPDATE tasks SET title = ?, description = ?, completed = ? WHERE id = ?",
             (data.get("title", task[1]), data.get("description", task[2]), data.get("completed", task[3]), task_id))
    
    return jsonify({"message": "Task updated successfully"})

# Route to delete a task
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = query_db("SELECT * FROM tasks WHERE id = ?", (task_id,), one=True)
    
    if not task:
        return jsonify({"error": "Task not found"}), 404

    query_db("DELETE FROM tasks WHERE id = ?", (task_id,))
    return jsonify({"message": "Task deleted successfully"})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
