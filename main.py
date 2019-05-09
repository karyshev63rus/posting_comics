from dotenv import load_dotenv
import json
import os
import requests
import random


url_vk_api = 'https://api.vk.com/method/'

def get_image():
	"""This function gets a random image from xkcd.com. and write it to a file."""
	current_image_num = requests.get('https://xkcd.com/info.0.json').json()['num']
	random_image_num = random.randint(0, current_image_num)
	random_image_url = 'https://xkcd.com/{}/info.0.json'.format(random_image_num)
	response = requests.get(random_image_url)
	image_url = response.json()['img']
	image_comment = response.json()['alt']
	image = requests.get(image_url)
	with open('image.jpg', 'bw') as file:
		file.write(image.content)
	with open('comment.txt', 'w') as file:
		file.write(image_comment)

def get_server_address():
    """This function gets upload_url data from a server for upload a photo."""
    server_address = requests.get(url_vk_api + 
    	'photos.getWallUploadServer', params=my_params)
    return server_address.json()['response']['upload_url']

def upload_photo_to_server():
	"""This function uploads a photo to a wall."""
	upload_url = get_server_address()
	files = {
	    'file': ('image.jpg', open('image.jpg', 'rb')), 
		'Content-Type': 'image/jpg', 
		'Content-Length': 1
	}
	upload_photo = requests.post(upload_url, 
		params=my_params, files=files)
	# image_file_descriptor.close()
	return (upload_photo.json()['server'],
		upload_photo.json()['photo'], 
		upload_photo.json()['hash'])

def save_photo_on_wall():
	"""This function saves a photo to a wall."""
	server, photo, hash_str = upload_photo_to_server()
	save_photo = requests.post(url_vk_api + 'photos.saveWallPhoto',
	    params={
	        'v': 5.95, 
	        'access_token': access_token, 
	        'user_id': user_id,
	        'client_id': client_id, 
	        'group_id': group_id, 
	        'server': server, 
	        'photo': photo, 
	        'hash': hash_str})
	return (save_photo.json()['response'][0]['id'],	
		save_photo.json()['response'][0]['owner_id'])
		    
def post_photo_on_wall():
	"""This function posts a photo and comment on a wall."""
	with open('comment.txt') as file:
		message = file.read()
	media_id, owner_id = save_photo_on_wall()
	post_photo = requests.get(url_vk_api + 'wall.post', 
		params={
		    'v': 5.95, 
		    'access_token': access_token, 
		    'type': 'photo', 
		    'client_id': client_id,
		    'owner_id': group_id, 
		    'from_group': 1, 
		    'attachments': {
		        'media_id': media_id,
		        'owner_id': -owner_id}, 
		    'message': message})
	return post_photo.json()

def main():
	get_image()
	print(post_photo_on_wall())
	os.remove('image.jpg')
	os.remove('comment.txt')

if __name__ == '__main__':

    load_dotenv()
    user_id = os.getenv('user_id')
    group_id = os.getenv('group_id')
    client_id = os.getenv('client_id')
    access_token = os.getenv('access_token')

    my_params = {
        'v': 5.95, 
        'user_id': user_id,
        'group_id': group_id,
        'client_id': client_id,
        'access_token': access_token
        }

    main()
