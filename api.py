import os
import time
from urllib.parse import urlparse
from pathlib import Path

import requests
from auth import get_auth


def get_resource_list(url, list_name=None, paginate=True):
    """
    Returns a list of HC resources specified by the url basename (such as .../articles.json)
    :param url: A full endpoint url, such as 'https://support.zendesk.com/api/v2/help_center/articles.json'
    :param list_name: The list name in the response per the docs. Required if list name not the same as resource name
    :param paginate: Whether the endpoint has pagination (i.e., a 'next_page' property). Example false: missing translations
    :return: List of resources, or False if the request failed
    """
    if list_name:
        resource = list_name
    else:
        resource = Path(url).stem
    record_list = {resource: []}
    while url:
        subdomain = urlparse(url).hostname.split('.')[0]
        response = requests.get(url, auth=get_auth(subdomain))
        if response.status_code == 429:
            print('Rate limited! Please wait.')
            time.sleep(int(response.headers['retry-after']))
            response = requests.get(url, auth=get_auth())
        if response.status_code != 200:
            print('Error with status code {}'.format(response.status_code))
            print(response.text)
            return False
        data = response.json()
        if data[resource]:  # guard against empty record list
            record_list[resource].extend(data[resource])
        if paginate:
            url = data['next_page']
        else:
            break
    return record_list[resource]


def get_resource(url, attachment=False):
    """
    Returns a single HC resource
    :param url: A full endpoint url, such as 'https://support.zendesk.com/api/v2/help_center/articles/2342572.json'
    :return: Dict of a resource, or False if the request failed.
    """
    resource = None
    subdomain = urlparse(url).hostname.split('.')[0]
    response = requests.get(url, auth=get_auth(subdomain))
    if response.status_code == 429:
        print('Rate limited! Please wait.')
        time.sleep(int(response.headers['retry-after']))
        response = requests.get(url, auth=get_auth())
    if response.status_code != 200:
        print('Failed to get record with error {}:'.format(response.status_code))
        print(response.text)
        return False
    if attachment == True:
        return response.content
    for k, v in response.json().items():
        resource = v
    if type(resource) is dict:
        return resource
    return None

def post_attachment(url, attachment, status=201):
    resource = None
    file = get_resource(attachment['content_url'], attachment=True)
    subdomain = urlparse(url).hostname.split('.')[0]
    file_path = os.path.join('attachments', attachment['file_name'])
    with open(file_path, 'wb') as f:
        f.write(file)
    with open(file_path, 'rb') as u:
        response = requests.post(url, data={'inline': attachment['inline']}, files={'file':u}, auth=get_auth(subdomain))
        if response.status_code == 429:
            print('Rate limited! Please wait.')
            time.sleep(int(response.headers['retry-after']))
            response = requests.post(url, files={'inline':attachment['inline'], 'file':u})
        if response.status_code != status:
            print('Failed to create record with error {}:'.format(response.status_code))
            print(response.text)
            return False
        for k, v in response.json().items():
            resource = v
        if type(resource) is dict:
            return resource
        return None


def post_resource(url, data, status=201):
    """
    :param url:
    :param data:
    :param status: HTTP status. Normally 201 but some POST requests return 200
    :return: Python data, or False if the request failed.
    """
    resource = None
    headers = {'Content-Type': 'application/json'}
    subdomain = urlparse(url).hostname.split('.')[0]
    response = requests.post(url, json=data, auth=get_auth(subdomain), headers=headers)
    if response.status_code == 429:
        print('Rate limited! Please wait.')
        time.sleep(int(response.headers['retry-after']))
        response = requests.post(url, json=data, auth=get_auth(), headers=headers)
    if response.status_code != status:
        print('Failed to create record with error {}:'.format(response.status_code))
        print(response.text)
        return False
    for k, v in response.json().items():
        resource = v
    if type(resource) is dict:
        return resource
    return None


def put_resource(url, data):
    """
    :param url:
    :param data:
    :return: Python data, or False if the request failed.
    """
    resource = None
    headers = {'Content-Type': 'application/json'}
    subdomain = urlparse(url).hostname.split('.')[0]
    response = requests.put(url, json=data, auth=get_auth(subdomain), headers=headers)
    if response.status_code == 429:
        print('Rate limited! Please wait.')
        time.sleep(int(response.headers['retry-after']))
        response = requests.post(url, json=data, auth=get_auth(), headers=headers)
    if response.status_code != 200:
        print('Failed to update record with error {}:'.format(response.status_code))
        print(response.text)
        return False
    for k, v in response.json().items():
        resource = v
    if type(resource) is dict:
        return resource
    return None


def delete_resource(url):
    """
    Runs a DELETE request on any Delete endpoint in the Zendesk API
    :param url: A full endpoint url, such as 'https://support.zendesk.com/api/v2/help_center/articles/2342572.json'
    :return: If successful, a 204 status code. If not, None
    """
    subdomain = urlparse(url).hostname.split('.')[0]
    response = requests.delete(url, auth=get_auth(subdomain))
    if response.status_code == 429:
        print('Rate limited! Please wait.')
        time.sleep(int(response.headers['retry-after']))
        response = requests.delete(url, auth=get_auth())
    if response.status_code != 204:
        print('Failed to delete record with error {}'.format(response.status_code))
        print(response.text)
        return False
    return None
