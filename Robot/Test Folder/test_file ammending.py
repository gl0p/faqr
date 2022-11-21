import json

string = 'bottle'
string_info = [1.234, -5.337, 'bottle']

blank_tag = {string_info[2]: [string_info[0], string_info[1]]}

with open('objects_last_locations.json', 'r+') as f:
    data = json.load(f)
    k = data['tag_names']
    print(k[1])



    #     x = read[string][0]
    #     y = read[string][1]
    #     k.pop(0)
    #     print(string, x, y)
    # else:
    #     print("Not in file")
    #
    # with open('objects_last_locations_names.json', 'w') as f:
    #     json.dump(data, f, indent=1)


def add_intent_name(name):
    # with open('intent_names.json', 'r+') as file:
    #     json.dump(tags, file, indent=1)
    with open('objects_last_locations_names.json', 'r') as f:
        data = json.load(f)
        k = data['tag_names']
        read = k[0]
        read[name] = name
    with open('objects_last_locations_names.json', 'w') as f:
        json.dump(data, f, indent=1)


def addRemove_resp_patterns(tag, pat_resp, message, app_rem):
    if app_rem == 1:
        with open('objects_last_locations.json', 'r') as f:
            data = json.load(f)
            k = data['intents']
            for x, obj in enumerate(k):
                if obj["tag"] == tag:
                    obj[f'{pat_resp}'].append(f'{message}')
    if app_rem == 0:
        with open('objects_last_locations.json', 'r') as f:
            data = json.load(f)
            k = data['tag']
            for x, obj in enumerate(k):
                if obj["tag"] == tag:
                    obj[f'{pat_resp}'].remove(f'{message}')

    with open('objects_last_locations.json', 'w') as f:
        json.dump(data, f, indent=1)


def add_tag(tag_name, patterns=[], responses=[]):
    flag = True
    blank_tag = {"tag": tag_name,
                 "patterns": patterns,
                 "responses": responses}

    with open('objects_last_locations.json', 'r+') as file:
        file_data = json.load(file)
        k = file_data["intents"]
        for x, obj in enumerate(k):
            if obj["tag"] == tag_name:
                flag = False
                print('Object already exists!')
                break
        if flag:
            file_data["tag"].append(blank_tag)
            file.seek(0)
            json.dump(file_data, file, indent=1)
            add_intent_name(tag_name)

def remove_tag(tag_name):
    with open('objects_last_locations.json', 'r') as file:
        file_data = json.load(file)
        k = file_data['tag']
        for indx, obj in enumerate(k):
            if obj['tag'] == tag_name:
                # print(obj)
                k.pop(indx)
    with open('objects_last_locations.json', 'w') as f:
        json.dump(file_data, f, indent=1)

    with open('objects_last_locations_names.json', 'r') as file:
        file_data = json.load(file)
        k = file_data['tag_names']
        k = k[0]
        for indx, obj in enumerate(k):
            if obj == tag_name:
                # print(obj)
                k.pop(obj)
                break
    with open('objects_last_locations_names.json', 'w') as f:
        json.dump(file_data, f, indent=1)



