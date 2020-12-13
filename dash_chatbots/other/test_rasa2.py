
# from rasa.cli.utils import print_success
# from rasa.nlu.model import Interpreter
# from rasa.nlu.utils import json_to_string

# # path of your model
# rasa_model_path = "<path-to-you-model-untar-directory>/nlu"

# # create an interpreter object
# interpreter = Interpreter.load(rasa_model_path)


# """
# Function to get model output
# Args:
#   text  (string)  --  input text string to be passed)
# For example: if you are interested in entities, you can just write result['entities']
# Returns:
#   json  --  json output to used for accessing model output
# """

# def rasa_output(text):
#     message = str(text).strip()
#     result = interpreter.parse(message)
#     return result
import requests
# print(rasa_output("Hi"))
payload = {'text':'hi how are you?'}
headers = {'content-type': 'application/json'}
r = requests.post('http://localhost:5005/model/parse', json=payload, headers=headers)