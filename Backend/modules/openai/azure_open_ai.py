from typing import Any, Dict
from openai import AzureOpenAI
from tenacity import retry , stop_after_attempt , wait_fixed , retry_if_exception_type
from config.config import azure_endpoint,api_key,api_version,model_deployment_name

client = AzureOpenAI(
    azure_endpoint=azure_endpoint,
    api_key=api_key,
    api_version=api_version
)

class CustomRetryException(Exception):
    pass

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type(CustomRetryException)
)
def make_request_json(message_text: list) -> dict:
    response = client.chat.completions.create(
        model=model_deployment_name,
        response_format={ "type": "json_object" },
        messages=message_text,
        temperature=0
    )
    return response.choices[0].message.content

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type(CustomRetryException)
)
def make_request(message_text: list) -> Dict[str, Any]:
    response = client.chat.completions.create(
        model=model_deployment_name,
        messages=message_text,
        temperature=0
    )
    return response.choices[0].message.content