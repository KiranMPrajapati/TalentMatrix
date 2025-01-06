import yaml 
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

def get_logger(name):
    return logging.getLogger(name)

# Load configuration file
def load_config(path='config.yaml'):
    with open(path, 'r') as file:
        CONFIG_DATA = yaml.load(file, Loader=yaml.FullLoader)
    return CONFIG_DATA

CONFIG_DATA = load_config(path='config.yaml')