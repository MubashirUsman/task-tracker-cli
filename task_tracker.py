import json, os, sys
from datetime import datetime

class TaskTracker:
    
    def add_task(self, task, file):
        if os.path.exists(file) is False or os.path.getsize(file) == 0:
            data = {"count": 0,
                    "tasks": {}}
            try:
                with open(file, mode="w", encoding="utf-8") as create_file:
                    json.dump(data, create_file, indent=4)
            except Exception as e:
                print(f"Error while creating file: {e}")
                return 1
            self.write_task(file, task)
        else:
            self.write_task(file, task)
        return 0

    def write_task(self, file, task):
        try:
            with open(file, mode="r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error while reading file: {e}")
            return 1
        data["count"] += 1
        data["tasks"][str(data["count"])] = {}
        data["tasks"][str(data["count"])]["name"] = task
        data["tasks"][str(data["count"])]["status"] = "to-do"
        data["tasks"][str(data["count"])]["created"] = f"Created: {str(datetime.now())}"
        data["tasks"][str(data["count"])]["updated"] = f"Updated: {str(datetime.now())}"
        try:
            with open(file, mode="w") as f:
                json.dump(data, f, indent=4)
                print(f"Task added successfully, ID: {data["count"]}")
        except Exception as e:
            print(f"Error while writing to file: {e}")
            return 1
    def update_task(self, id, status, file): # for done and in-progress
        id = str(id)
        with open(file, mode="r", encoding="utf-8") as f:
            data = json.load(f)
        if id not in data["tasks"]:
            print( f"ID {id} not found")
            return 1
        data["tasks"][id]["status"] = status
        data["tasks"][id]["updated"] = f"Updated: {str(datetime.now())}"
        with open(file, mode="w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            print(f"Task {id} updated!!")
        return 0
    
    def delete_task(self, id, file):
        id = str(id)
        try:
            with open(file, mode="r", encoding="utf-8") as f:
                data = json.load(f)
            try:
                data["tasks"].pop(id)
                print(f"Task with {id} was deleted successfully.")
            except KeyError:
                print(f"Task with ID {id} could not be found")
            with open(file, mode="w", encoding="utf-8") as wf:
                json.dump(data, wf, indent=4)
        except Exception as e:
            print(f"Error while reading file or deleting key, {e}")
            return 1

    def list_task(self, file, status = None):
        try:
            with open(file, mode="r", encoding="utf-8") as rf:
                tasks = json.load(rf)["tasks"]
        except FileNotFoundError:
            print("Could not find the file.")
            return 1
        list_of_tasks = []
        if status is not None and status in ["to-do", "in-progress", "done"]:
            for id, task in tasks.items():
                # print(task)
                if task["status"] == status:
                    list_of_tasks.append(task["name"])
        if status is None:
            for _, task in tasks.items():
                list_of_tasks.append(task["name"])
        print("\n".join(list_of_tasks))
        return 0


if __name__ == "__main__":
    task_tracker = TaskTracker()
    action = sys.argv[1]
    if action == "add":
        task_name = sys.argv[2]
        task_tracker.add_task(task_name, "tasks.json")
    if action == "update":
        task_id = sys.argv[2]
        task_name = sys.argv[3]
        task_tracker.update_task(task_id, task_name, "tasks.json")
    if action in ["mark-done", "mark-in-progress"]:
        task_id = sys.argv[2]
        status = "done" if action == "mark-done" else "in-progress"
        task_tracker.update_task(task_id, status, "tasks.json")
    if action == "delete":
        task_id = sys.argv[2]
        task_tracker.delete_task(task_id, "tasks.json")
    if action == "list":
        if len(sys.argv) == 3:
            status = sys.argv[2]
            task_tracker.list_task("tasks.json", status)
        else:
            task_tracker.list_task("tasks.json")
