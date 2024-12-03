from pymongo import MongoClient

def get_database():
    # conexion al servidor lcal de mongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["task_manager"]
    return db