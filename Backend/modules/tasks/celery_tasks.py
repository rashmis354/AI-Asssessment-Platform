from modules.celery_config import app
from modules.openai.azure_open_ai import make_request

@app.task
def openai_celery_task(openai_obj):
    print("open_ai_celery_task")
    result = make_request(openai_obj)
    print(result)
    return result