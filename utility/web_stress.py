import random
import requests
import time

with open("web_stress.txt", "r") as f:
    objects = f.readlines()

while True:
    name = objects[random.randint(0, len(objects))].strip()
    url = f"https://lasair-lsst-dev.lsst.ac.uk/objects/{name}/"
    print('Getting', url)
    start_time = time.perf_counter()
    content = requests.get(url)
    end_time = time.perf_counter()
    print(f"Status {content.status_code}, {len(content.content)}b, {end_time - start_time:.2f} s")


