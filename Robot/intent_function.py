import json
from neuralintents import GenericAssistant
from time import sleep

### function_to_append_json(tag, pattern or response, message, add or remove)

# tags = {"tag_names": [{"greeting": 0, "goodbye": 1, "search": 2, "personal": 3}]}


def add_intent_name(name):
    # with open('intent_names.json', 'r+') as file:
    #     json.dump(tags, file, indent=1)
    with open('intent_names.json', 'r') as f:
        data = json.load(f)
        k = data['tag_names']
        read = k[0]
        read[name] = name
    with open('intent_names.json', 'w') as f:
        json.dump(data, f, indent=1)


def addRemove_resp_patterns(tag, pat_resp, message, app_rem):
    if app_rem == 1:
        with open('intents.json', 'r') as f:
            data = json.load(f)
            k = data['intents']
            for x, obj in enumerate(k):
                if obj["tag"] == tag:
                    obj[f'{pat_resp}'].append(f'{message}')
    if app_rem == 0:
        with open('intents.json', 'r') as f:
            data = json.load(f)
            k = data['intents']
            for x, obj in enumerate(k):
                if obj["tag"] == tag:
                    obj[f'{pat_resp}'].remove(f'{message}')

    with open('intents.json', 'w') as f:
        json.dump(data, f, indent=1)


def add_tag(tag_name, patterns=[], responses=[]):
    flag = True
    blank_tag = {"tag": tag_name,
                 "patterns": patterns,
                 "responses": responses}

    with open('intents.json', 'r+') as file:
        file_data = json.load(file)
        k = file_data["intents"]
        for x, obj in enumerate(k):
            if obj["tag"] == tag_name:
                flag = False
                print(f'{tag_name} object already exists!')
                sleep(1)
                break
        if flag:
            file_data["intents"].append(blank_tag)
            file.seek(0)
            json.dump(file_data, file, indent=1)
            add_intent_name(tag_name)


def train_assistant(name):
    assistant = GenericAssistant('intents.json', model_name=name)
    assistant.train_model()
    assistant.save_model()


def remove_tag(tag_name):
    with open('intents.json', 'r') as file:
        file_data = json.load(file)
        k = file_data['intents']
        for indx, obj in enumerate(k):
            if obj['tag'] == tag_name:
                # print(obj)
                k.pop(indx)
    with open('intents.json', 'w') as f:
        json.dump(file_data, f, indent=1)

    with open('intent_names.json', 'r') as file:
        file_data = json.load(file)
        k = file_data['tag_names']
        k = k[0]
        for indx, obj in enumerate(k):
            if obj == tag_name:
                # print(obj)
                k.pop(obj)
                break
    with open('intent_names.json', 'w') as f:
        json.dump(file_data, f, indent=1)


# remove_tag('quit')
# add_tag('test')
# addRemove_resp_patterns('test', 'responses', 'holy fuck it is you!', 1)
# add_tag('give_up',
#         ['give up'],
#         [''])



train_assistant("speech_response_model_V1")




