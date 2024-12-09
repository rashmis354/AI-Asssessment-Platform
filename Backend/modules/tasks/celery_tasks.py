import json
from modules.celery_config import app
from modules.openai.azure_open_ai import make_request_json

@app.task
def openai_celery_task(openai_obj):
    print("open_ai_celery_task")
    result = make_request_json(openai_obj)
    formatted_result = json.loads(result)
    print(formatted_result)
    return formatted_result