import os, sys, json
for file in os.listdir('.'):
    if file.endswith('_object.json'):
        print(file)
        p = json.loads(open(file).read())
        for k,v in p.items():
            if k.startswith('jump'):
                print(k, v)
