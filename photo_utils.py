import os
import requests

from config import memes_folder

if memes_folder.strip('./') not in os.listdir():
    os.mkdir(memes_folder)

sizes = ['w', 'z', 'y', 'r', 'q', 'p', 'o', 'x', 'm', 's']


def get_filename():
    return str(max(map(lambda x: int(x.strip('.png')), os.listdir(memes_folder))) + 1) + '.png'


def download(photo_data, path_to=memes_folder):
    url = None
    for i in sizes:
        if url:
            break
        for sz in photo_data['sizes']:
            if sz['type'] == i:
                url = sz['url']
                break
    filename = path_to + '/' + get_filename()
    img_data = requests.get(url).content
    with open(filename, 'wb') as f:
        f.write(img_data)
    return filename

