import os
import yaml
from dotenv import load_dotenv
load_dotenv()


class YamlParser(yaml.YAMLObject):
    yaml_loader = yaml.SafeLoader
    yaml_tag = '!Parse'

    @classmethod
    def from_yaml(cls, loader, node):
        concat_value = ""
        for item in node.value:
            if "os.environ.get" in str(item.value):
                env_value = eval(item.value)
                concat_value += env_value
            else:
                concat_value += item.value
        return concat_value
    
yaml.SafeLoader.add_constructor('!Parse', YamlParser.from_yaml)

config_path = os.getcwd()
config_details = yaml.safe_load(open(config_path + "/config/config.yaml"))

LOGS_PATH = config_details['LOGS_PATH']
LOGS_FOLDER_NAME = config_details['LOGS_FOLDER_NAME']
LOG_FILE_BASE_NAME = config_details['LOG_FILE_BASE_NAME']
default_log_level = config_details['default_log_level']
backupCount = config_details['backupCount']
file_rotation = config_details['file_rotation']
file_rotation_interval = config_details['file_rotation_interval']

STATUS_FAILURE = config_details['STATUS_FAILURE']
STATUS_SUCCESS = config_details['STATUS_SUCCESS']

code_review_prompt = config_details['code_review_prompt']
code_review_user_prompt = config_details['code_review_user_prompt']

azure_endpoint = config_details ['azure_endpoint']
api_key = config_details ['api_key']
api_version = config_details ['api_version']
model_deployment_name = config_details ['model_deployment_name']

# assessment_data_model = config_details['']['assessment_data_model']


nosql_connection_string = config_details['nosql_connection_string']
nosql_db_name = config_details['nosql_db_name']

database_type = config_details['database_type']
database_server = config_details['database_server']
database_name = config_details['database_name']
database_username = config_details['database_username']
database_password = config_details['database_password']