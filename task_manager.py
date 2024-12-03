from bson.objectid import ObjectId

# metodo para crear una tarea en la base de datos
def create_task(db, name, description, due_date, status="pending"):
    # crea un diccionario con la informacion de la tarea 
    task = {
        "name":name, 
        "description": description, 
        "due_date": due_date, 
        "status": status
    }
    # inserta la tarea en la coleccion tasks
    db["tasks"].insert_one(task)
    print(f"Tarea '{name}' creada con exito")


# metodo para actualizar el estado de una tarea existente
def update_task_status(db, task_id, new_status):
    # busca la tarea por su ID de MongoDB y actualiza su sestado 
    result = db["tasks"].update_one(
        {"_id": ObjectId(task_id)}, 
        {"$set": {"status": new_status}}
    )
    if result.modified_count > 0:
        print("Estado actualizado correctamente")
    else:
        print("No se encontro la tarea")
    

# metodo para listar todas las tareas 
def list_tasks(db):
    # recupera todas las tareas de la coleccion
    tasks = db["tasks"].find()
    for task in tasks:
        print(f"{task['_id']} - {task['name']} - {task['status']}")


#metodo para generar estadisticas de las tareas
def generate_statistics(db):
    # cuanta el numero total de tareas 
    total = db["tasks"].count_documents({})
    # cuenta las tareas completadas
    completed = db["tasks"].count_documents({"status": "completed"})
    # cuenta las tareas pendintes
    pending = db["tasks"].count_documents({"status":"pending"})
    return total, completed, pending