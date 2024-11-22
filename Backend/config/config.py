import os
import yaml

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
