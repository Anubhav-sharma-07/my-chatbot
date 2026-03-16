import json
import os

MEMORY_FILE = "client_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def remember_client(name, info):
    memory = load_memory()
    if name not in memory:
        memory[name] = {}
    memory[name].update(info)
    save_memory(memory)

def get_client(name):
    memory = load_memory()
    return memory.get(name, None)

def get_all_clients():
    return load_memory()
