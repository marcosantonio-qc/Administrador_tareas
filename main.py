# import necessary flask modyuls and custom modules
import os
from flask import Flask, render_template, request, redirect
from db import get_database # custom database connection module
from task_manager import create_task, update_task_status, list_tasks, generate_statistics

# initialize flask application
app = Flask(__name__)

# stablish database connection 
db = get_database()

# route for home page
@app.route("/")
def home():
    # render the main index page 
    return render_template("index.html")



# route to handle tasks - supports both viewing and creating tasks 
@app.route("/tasks", methods = ["GET", "POST"])

def tasks():
    # handle task creation when POST request is received 
    if request.method == "POST":

        # Extract task details from task submition
        name = request.form["name"]
        description = request.form["description"]
        due_date = request.form["due_date"]

        # create new task in the database
        create_task(db, name, description, due_date)

        # redirect to task page to prevent form resubmission
        return redirect("/tasks")
    
    # retrieve all tasks when GET request is received 
    all_tasks = list(db["tasks"].find())

    # render task page with retrieved tasks
    return render_template("tasks.html", tasks=all_tasks)



# route to update task status
@app.route("/update_status/<task_id>", methods=["POST"])

def update_status(task_id):
    # get new status from form submission 
    new_status = request.form["new_status"]

    # update task status in the database, metodo del 
    update_task_status(db, task_id, new_status)

    # redirigir a la pagina de tareas
    return redirect("/tasks")



# ruta para mostrar estadisticas 
@app.route("/stats")

def stats():
    #obtener estadisticas de tareas
    total, completed, pending = generate_statistics(db)

    # renderizar pagina de estadisticas
    return render_template("stats.html", total=total, completed = completed, pending = pending)

# ejecutar la aplicacion en modo debug
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
    



