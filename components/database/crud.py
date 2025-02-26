from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

'''
DB - TODOBOT

Collection 1: TODOLIST

Fields: _id, category, title, description, due_date, priority, status, created_at, remainder_system, modified_at, is_human

Operations:
    add_task(category, title, description, due_date, priority, status, created_at, remainder_system, is_human)
    update_category(task_id, new_category)
    update_task_title(task_id, new_title)
    update_task_description(task_id, new_description)
    update_task_due_date(task_id, new_due_date)
    update_task_priority(task_id, new_priority)
    update_task_status(task_id, new_status)
    update_task_remainder_system(task_id, new_remainder_system)

    delete_task(task_id)

    get_task_details(task_id)
    get_all_tasks_by_category(category)

    get_overdue_tasks()
    get_tasks_by_priority(priority)
    get_tasks_by_due_date(due_date)

Notes:

- modified_at is the time when the task was updated. 
- While task creation, modified_at is same as task creation_at

Collection 2: Categories Collection
'''

client = MongoClient('mongodb://localhost:27017/')

db = client['TODOBOT']

todo_list_collection = db['TODOLIST']

def add_category(category):
    todo_list_collection.insert_one({'category': category})

def add_task(category, title, description, due_date, priority, status, created_at, remainder_system, is_human):
    task = {
        'category': category,
        'title': title,
        'description': description,
        'due_date': due_date,
        'priority': priority,
        'status': status,
        'created_at': created_at,
        'remainder_system': remainder_system,
        'modified_at': created_at,
        'is_human': is_human
    }

    todo_list_collection.insert_one(task)
    print(f'Task added successfully: {task["title"]}')

def add_task_with_dictionary(task):
    todo_list_collection.insert_one(task)
    print(f'Task added successfully: {task["title"]}')

def update_category(task_id, new_category):
    updated_task = {
        '$set': {
            'category': new_category,
            'modified_at': datetime.now()
        }
    }

    todo_list_collection.update_one({'_id': task_id}, updated_task)
    print(f'Task category updated successfully: {task_id}')

def update_task_title(task_id, new_title):
    task_id = ObjectId(task_id)

    updated_task = {
        '$set': {
            'title': new_title,
            'modified_at': datetime.now()
        }
    }

    todo_list_collection.update_one({'_id': task_id}, updated_task)
    print(f'Task title updated successfully: {task_id}')

def update_task_description(task_id, new_description):
    task_id = ObjectId(task_id)

    updated_task = {
        '$set': {
            'description': new_description,
            'modified_at': datetime.now()
        }
    }

    todo_list_collection.update_one({'_id': task_id}, updated_task)
    print(f'Task description updated successfully: {task_id}')

def update_task_due_date(task_id, new_due_date):
    task_id = ObjectId(task_id)

    updated_task = {
        '$set': {
            'due_date': new_due_date,
            'modified_at': datetime.now()
        }
    }

    todo_list_collection.update_one({'_id': task_id}, updated_task)
    print(f'Task due date updated successfully: {task_id}')

def update_task_priority(task_id, new_priority):
    task_id = ObjectId(task_id)

    updated_task = {
        '$set': {
            'priority': new_priority,
            'modified_at': datetime.now()
        }
    }

    todo_list_collection.update_one({'_id': task_id}, updated_task)
    print(f'Task priority updated successfully: {task_id}')

def update_task_status(task_id, new_status):
    task_id = ObjectId(task_id)

    updated_task = {
        '$set': {
            'status': new_status,
            'modified_at': datetime.now()
        }
    }

    todo_list_collection.update_one({'_id': task_id}, updated_task)
    print(f'Task status updated successfully: {task_id}')

def update_task_remainder_system(task_id, new_remainder_system):
    task_id = ObjectId(task_id)

    updated_task = {
        '$set': {
            'remainder_system': new_remainder_system,
            'modified_at': datetime.now()
        }
    }

    todo_list_collection.update_one({'_id': task_id}, updated_task)
    print(f'Task remainder system updated successfully: {task_id}')

def delete_task(task_id):
    task_id = ObjectId(task_id)
    todo_list_collection.delete_one({'_id': task_id})
    print(f'Task deleted successfully: {task_id}')

def delete_all_tasks():
    todo_list_collection.delete_many({})
    print('All tasks deleted successfully.')

def get_task_details(task_id):
    task = todo_list_collection.find_one({'_id': ObjectId(task_id)})

    print(f"ERROR: Task {task} not found")
    
    return task

def get_all_tasks_by_category(category):
    tasks = todo_list_collection.find({'category': category})
    
    return tasks

def get_overdue_tasks():
    overdue_tasks = todo_list_collection.find({'due_date': {'$lt': datetime.now()}, 'status': 'Not Started'})
    
    return overdue_tasks

def get_tasks_by_priority(priority):
    tasks = todo_list_collection.find({'priority': priority})
    
    return tasks

def get_all_tasks():
    tasks = todo_list_collection.find()

    tasks_list = []

    for task in tasks.clone():
        tasks_list.append(task)

    for index in range(0, len(tasks_list)):
        tasks_list[index] = convert_to_datetime(tasks_list[index])
    
    return tasks_list

def insert_10_samples():
    samples = [
    {
        "category": "Work",
        "title": "Complete project report",
        "description": "Write a comprehensive report on the recent project.",
        "due_date": "2024-10-25 14:00",
        "priority": "High",
        "status": "Pending",
        "created_at": "2024-10-15 15:00",
        "remainder_system": "Email",
        "modified_at": "2024-10-15 16:00",
        "is_human": True
    },
    {
        "category": "Personal",
        "title": "Grocery shopping",
        "description": "Buy milk, eggs, bread, and fruits.",
        "due_date": "2024-10-23 14:00",
        "priority": "Medium",
        "status": "Pending",
        "created_at": "2024-10-20 15:00",
        "remainder_system": "Push notification",
        "modified_at": "2024-10-20 16:00",
        "is_human": True
    },
    {
        "category": "Work",
        "title": "Attend team meeting",
        "description": "Discuss project updates and next steps.",
        "due_date": "2024-10-22 14:00",
        "priority": "Low",
        "status": "Completed",
        "created_at": "2024-10-18 15:00",
        "remainder_system": "Email",
        "modified_at": "2024-10-18 16:00",
        "is_human": True
    },
    {
        "category": "Personal",
        "title": "Schedule doctor's appointment",
        "description": "Make an appointment for a check-up.",
        "due_date": "2024-10-28 14:00",
        "priority": "High",
        "status": "Pending",
        "created_at": "2024-10-21 15:00",
        "remainder_system": "Push notification",
        "modified_at": "2024-10-21 16:00",
        "is_human": True
    },
    {
        "category": "Work",
        "title": "Review code changes",
        "description": "Check for errors and potential improvements in the code.",
        "due_date": "2024-10-24 14:00",
        "priority": "Medium",
        "status": "Pending",
        "created_at": "2024-10-22 15:00",
        "remainder_system": "Email",
        "modified_at": "2024-10-22 16:00",
        "is_human": True
    }
    ]

    todo_list_collection.insert_many(samples)
    print("10 sample tasks inserted successfully.")

def convert_to_datetime(data):
    date_fields = ['due_date', 'created_at', 'modified_at']
    for field in date_fields:
        if field in data and isinstance(data[field], str):
            data[field] = datetime.strptime(data[field], '%Y-%m-%d %H:%M')
    return data

# Function to convert datetime fields back to string format
def convert_to_string(data):
    date_fields = ['due_date', 'created_at', 'modified_at']
    for field in date_fields:
        if field in data and isinstance(data[field], datetime):
            data[field] = data[field].strftime('%Y-%m-%d %H:%M')
    return data

# Get all categories

def get_categories():
    categories = todo_list_collection.distinct("category")
    return list(categories)

# delete_all_tasks()

# insert_10_samples()

tasks = get_all_tasks()

for task in tasks:
    print(task['_id'])
    print(f"Task Category: {task['category']}")
    print(f"Task Title: {task['title']}")
    print(f"Task Description: {task['description']}")
    print(f"Task Due Date: {task['due_date']}")
    print(f"Task Priority: {task['priority']}")
    print(f"Task Status: {task['status']}")
    print(f"Task Created At: {task['created_at']}")
    print(f"Task Modified At: {task['modified_at']}")
    print(f"Task Remainder System: {task['remainder_system']}")
    print(f"Task Is Human: {type(task['is_human'])}")
    print("--------------------")

# delete_task("67259a3e67d0bcca1dc31006")