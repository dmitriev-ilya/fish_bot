import os

import requests
from dotenv import load_dotenv


def get_access_token(client_id, client_secret):
    api_access_url = 'https://useast.api.elasticpath.com/oauth/access_token'
    api_access_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(api_access_url, data=api_access_data)
    response.raise_for_status()

    access_token = response.json()['access_token']
    return access_token


def get_implicit_access_token(client_id):
    api_access_url = 'https://useast.api.elasticpath.com/oauth/access_token'
    api_access_data = {
        'client_id': client_id,
        'grant_type': 'implicit'
    }
    response = requests.post(api_access_url, data=api_access_data)
    response.raise_for_status()

    access_token = response.json()['access_token']
    return access_token


def get_products(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    product_api_base_url = 'https://useast.api.elasticpath.com/pcm/products'
    params = {
        'productId': "", 
        'include': 'component_products'
    }

    responce = requests.get(product_api_base_url, params=params, headers=headers)
    return responce.json()


def get_product(access_token, product_id):
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    product_api_base_url = f'https://useast.api.elasticpath.com/pcm/products/{product_id}'

    responce = requests.get(product_api_base_url, headers=headers)
    return responce.json()


def create_cart(access_token, cart_id):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    cart_api_url = 'https://useast.api.elasticpath.com/v2/carts'
    cart_data = {
        'data': {
            'name': f'{cart_id}',
            'id': cart_id
        }
    }

    create_cart_responce = requests.post(cart_api_url, json=cart_data, headers=headers)
    create_cart_responce.raise_for_status()
    return create_cart_responce.json()


def get_cart(access_token, cart_id):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    cart_url = f'https://useast.api.elasticpath.com/v2/carts/{cart_id}'

    geting_cart_response = requests.get(cart_url, headers=headers)
    geting_cart_response.raise_for_status()
    return geting_cart_response.json()


def get_cart_items(access_token, cart_id):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    cart_items_url = f'https://useast.api.elasticpath.com/v2/carts/{cart_id}/items'

    response = requests.get(cart_items_url, headers=headers)
    response.raise_for_status()
    return response.json()


def add_cart_item(access_token, cart_id, product_id, quantity):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    item_data = {
        'data': {
            'id': product_id,
            'type': 'cart_item',
            'quantity': quantity
        }
    }
    cart_items_url = f'https://useast.api.elasticpath.com/v2/carts/{cart_id}/items'

    adding_cart_item_response = requests.post(cart_items_url, headers=headers, json=item_data)
    adding_cart_item_response.raise_for_status()
    return adding_cart_item_response.json()


def get_file_href(access_token, file_id):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    getting_file_api_url = f'https://useast.api.elasticpath.com/v2/files/{file_id}'

    response = requests.get(getting_file_api_url, headers=headers)
    response.raise_for_status()
    return response.json()['data']['link']['href']


if __name__ == '__main__':
    load_dotenv()

    access_token = get_access_token(os.getenv('CLIENT_ID'), os.getenv('CLIENT_SECRET'))

    losos_id = 'efe48323-9521-408a-9bfc-b673dc8a2725'

    print(get_product(access_token, losos_id))
