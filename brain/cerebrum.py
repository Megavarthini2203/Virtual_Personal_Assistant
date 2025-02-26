from transformers import AutoTokenizer, AutoModelForSequenceClassification
import json
import google.generativeai  as genai
from datetime import datetime
import torch

model2 = AutoModelForSequenceClassification.from_pretrained("roberta-base", num_labels=2) # adjust for your model specifics
model2.load_state_dict(torch.load("brain/model/model_weights.pth", map_location=torch.device('cpu')))

tokenizer_save_dir = 'brain/tokenizer'
tokenizer2 = AutoTokenizer.from_pretrained(tokenizer_save_dir)

def relevance_score(message_body):
    inputs = tokenizer2(message_body, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model2(**inputs)
        logits = outputs.logits

    predicted_label = torch.argmax(logits, dim=1).item()

    return predicted_label

def create_prompt(formatted_time, catagories_string, message):

    prompt1 = """
    **Prompt**: 

    The provided dataset complies with ethical standards and is safe for research purposes. Your task is to extract specific information from a given message (ACTUAL_MESSAGE) and return it in a JSON format with the following structure.

    **Example**:

    **Categories**: "Data Analytics", "Deep Learning"  
    **Sample Message**: "Guys, try to submit your DA record notebook by tomorrow at 14:00."

    **Expected JSON Output**:
    ```json
    {
        "Category": "Data Analytics DA", // Choose from the categories given (when choosing don't modify the text) or create a new one if necessary
        "Title": "Data Analytics Record Submission", // Create a suitable title for the task
        "Description": "Submit your DA record notebook by tomorrow.", // Provide a concise and grammatically accurate description
        "Priority": "High", // Estimate priority based on urgency and due date
        "Due": "16-10-2024 14:00" // Convert any due date info to this format; if not present, set to "None": Note: "If time is not present, simply give 00:00 at the end"
    }
    ```
    """
    prompt2 = f"""
    **Your Task**:

    Today's Date: **{formatted_time}**  
    **Categories**: {catagories_string}  
    **Message**: "{message}"
    """
    prompt3 = """
    **Output**:  
    Provide only the JSON in the format below:
    ```json
    {
        "Category": "",
        "Title": "",
        "Description": "",
        "Priority": "",
        "Due": ""
    }
    ```
    Try to understand the context while creating new categories. Try varieties of categories while being consistant.
    Try to guess or provide an appropriate due datetime based on the context. Datetime Format - %Y-%m-%d %H:%M.
    Do not include any additional commentary or text outside of the JSON response.
    """

    return prompt1 + prompt2 + prompt3

def parse_task_string(task_string: str):
    task_string = task_string[8:-4].strip()
    task_dict = json.loads(task_string)
    
    due_str = task_dict.get("Due")
    if due_str != 'None':
        task_dict["Due"] = datetime.strptime(due_str, '%Y-%m-%d %H:%M')
    else:
        task_dict["Due"] = None
    
    return task_dict

def extract_using_gemini(formatted_time, catagories_string, message, feedback=""):
    API_KEY = '' # Need to add this!
    genai.configure(api_key=API_KEY)

    feedback = "\nFeedback:\n " + feedback

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(create_prompt(formatted_time=formatted_time, catagories_string=catagories_string, message=message) + feedback)
    text = response.text
    result = parse_task_string(text)

    return(result)

from pymongo import MongoClient
from datetime import datetime

def mark_relavance_and_process():

    UPDATION_STATUS = False

    client = MongoClient('mongodb://localhost:27017/')
    db = client['whatsapp']
    collection = db['messages']

    db2 = client['TODOBOT']
    todo_list_collection = db2['TODOLIST']

    collection.update_many(
        {'isProcessed': {'$exists': False}},
        {'$set': {'isProcessed': False}}
    )

    collection.update_many(
        {'isRelevant': {'$exists': False}},
        {'$set': {'isRelevant': False}}
    )

    unprocessed_documents = collection.find({'isRelevant': False})

    for doc in unprocessed_documents:
        print(doc['body'])
        boolean = bool(relevance_score(doc['body']))
        print(f"Relevance Score: {boolean}")
        print("-------------------------------")
        collection.update_one(
            {'_id': doc['_id']},
            {'$set': {'isRelevant': boolean}}
        )

    collection.delete_many({'isRelevant': False})

    relevant_documents = collection.find({'isProcessed': False})

    categories = todo_list_collection.distinct("category")


    for doc in relevant_documents:
        timestamp = doc['timestamp']
        readable_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

        message = doc['body']

        result = extract_using_gemini(readable_time, categories, message)

        today = datetime.now()
        
        duedate = result['Due']

        if duedate is not None:
            if duedate > today:
                status = "Pending"
            elif duedate == today:
                status = "Pending"
            else:
                status = "Past Due"
        else:
            status = "Unknown"

        TASK = {
            "message_id" : doc['messageId'],
            "category": result['Category'],
            "title": result['Title'],
            "description": result['Description'],
            "due_date": result['Due'],
            "priority": result['Priority'],
            "status": status,
            "created_at": today,
            "remainder_system": "WhatsApp",
            "modified_at": today,
            "is_human": False,
            "is_notified": False,
            "next_notification_slot": result['Due']
        }

        todo_list_collection.insert_one(TASK)
        UPDATION_STATUS = True

        collection.update_one(
            {'_id': doc['_id']},
            {'$set': {'isProcessed': True}}
        )

    return UPDATION_STATUS

# mark_relavance_and_process()

if __name__ == '__main__':
    mark_relavance_and_process()
