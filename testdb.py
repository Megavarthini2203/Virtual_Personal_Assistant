from pymongo import MongoClient

# Function to query and print all data from the collections
def query_all_data():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['whatsapp']
    collection = db['messages']

    db2 = client['TODOBOT']
    todo_collection = db2['TODOLIST']
    update_collection = collection['updates']

    # Step 1: Fetch and print all data from updates collection
    print("All data from the 'updates' collection:")
    updates = update_collection.find()
    for update in updates:
        print(update)
    print()
    msgs = collection.find()
    for msg in msgs:
        print(msg)
    # Step 2: Fetch and print all data from todo_list collection
    print("\nAll data from the 'todo_list' collection:")
    todos = todo_collection.find()
    for todo in todos:
        print(todo)

   

# Run the function
if __name__ == "__main__":
    query_all_data()
