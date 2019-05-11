from dotenv import load_dotenv
import json
import os
import requests
import random


url_vk_api = 'https://api.vk.com/method/'


def get_image_content_and_comment() -> tuple:
    """It gets a random image from xkcd.com. and write it to a file."""
    current_image_num = requests.get('https://xkcd.com/info.0.json').json()['num']
    random_image_num = random.randint(0, current_image_num)
    random_image_url = 'https://xkcd.com/{}/info.0.json'.format(random_image_num)
    response = requests.get(random_image_url)
    response.raise_for_status()
    image_url = response.json()['img']
    image_comment = response.json()['alt']
    image = requests.get(image_url)
    image.raise_for_status()
    image_content = image.content
    return (image_content, image_comment)

def write_image_content_and_comment() -> object:
    """It write image content and comment fron xkcd.com site."""
    image_content, image_comment = get_image_content_and_comment()
    with open('image.jpg', 'bw') as file:
        file.write(image_content)
    with open('comment.txt', 'w') as file:
        file.write(image_comment)

def get_server_address() -> str:
    """It gets upload_url data from a server for upload a photo."""
    server_address = requests.get(url_vk_api + 
        'photos.getWallUploadServer', params=my_params)
    server_address.raise_for_status()
    upload_url = server_address.json()['response']['upload_url']
    return upload_url

def upload_photo_to_server() -> tuple:
    """It uploads a photo to a wall."""
    upload_url = get_server_address()
    files = {
        'file': ('image.jpg', open('image.jpg', 'rb')), 
        'Content-Type': 'image/jpg', 
        'Content-Length': 1
    }
    upload_photo = requests.post(upload_url, params=my_params, files=files)
    upload_photo.raise_for_status()
    server = upload_photo.json()['server']
    photo = upload_photo.json()['photo']
    hash_str = upload_photo.json()['hash'] 
    return (server, photo, hash_str)

def save_photo_on_wall() -> tuple:
    """It saves a photo to a wall."""
    server, photo, hash_str = upload_photo_to_server()
    save_photo = requests.post(url_vk_api + 'photos.saveWallPhoto',
        params={
            'v': 5.95, 
            'access_token': access_token, 
            'user_id': user_id,
            'group_id': group_id, 
            'server': server, 
            'photo': photo, 
            'hash': hash_str
        })
    save_photo.raise_for_status()
    media_id = save_photo.json()['response'][0]['id']
    owner_id = save_photo.json()['response'][0]['owner_id']
    return (media_id, owner_id)
      
def read_saved_comment() -> object:
    """"It reads comment that have saved duiring write image content."""
    with open('comment.txt') as file:
        message = file.read()
    return message

def post_photo_on_wall() -> dict:
    """It posts a photo and comment on a wall."""
    message = read_saved_comment()
    media_id, owner_id = save_photo_on_wall()
    post_photo = requests.get(url_vk_api + 'wall.post', 
        params={
            'v': 5.95, 
            'access_token': access_token, 
            'type': 'photo', 
            'owner_id': group_id, 
            'from_group': 1, 
            'attachments': {
                'media_id': media_id,
                'owner_id': -owner_id
            }, 
            'message': message
        })
    post_photo.raise_for_status()
    result_of_posting = post_photo.json()
    return result_of_posting

def main():
    """It supervises work of all functions."""
    try:
        get_image_content_and_comment()
        write_image_content_and_comment()
        print(post_photo_on_wall())
        os.remove('image.jpg')
        os.remove('comment.txt')
    except requests.RequestException as err:
        print(err.response)

if __name__ == '__main__':

    load_dotenv()
    user_id = os.getenv('user_id')
    group_id = os.getenv('group_id')
    access_token = os.getenv('access_token')

    my_params = {
        'v': 5.95, 
        'user_id': user_id,
        'group_id': group_id,
        'access_token': access_token
    }

    main()
