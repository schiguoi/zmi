import os
import json
import configparser
import requests

import api

# ----- Functions ----- #

def get_settings():
    config = configparser.ConfigParser()
    config.read('settings.ini')
    default = config['DEFAULT']
    settings = {'cross_instance': default['cross_instance'],
                'src_kb': default['src_kb'],
                'dst_kb': default['dst_kb'],
                'src_root': 'https://{}.zendesk.com/api/v2/help_center'.format(default['src_kb']),
                'dst_root': 'https://{}.zendesk.com/api/v2/help_center'.format(default['dst_kb']),
                'locale': default['locale'],
                'team_user': default['team_user'],
                'notify_articles': default['notify_articles']}
    return settings


def read_data(file_name):
    """
    Reads a .json file and converts it to a Python data structure
    :param file_name: File in the data folder. Omit the .json extension. One of "articles", "sections",
     "comments", "subscriptions", "votes"
    :return: Python data structure
    """
    file_path = os.path.join('data', f'{file_name}.json')
    if os.path.isfile(file_path) is False:
        print(f'File does not exist: {file_name}')
        exit()
    with open(file_path, mode='r') as f:
        data = json.load(f)
    return data


def write_data(data, resources):
    """
    Writes a Python data structure to a .json file
    :param data: A Python data structure
    :param resources: One of "articles", "sections", "comments", "subs", etc
    :return: None
    """
    file_path = os.path.join('data', f'{resources}.json')
    with open(file_path, mode='w') as f:
        json.dump(data, f, sort_keys=True, indent=2)


def package_article(article, put=False, notify=False):
    """
    Creates the payload for a PUT or POST article request.
    :param article: Complete article dict from API
    :param put: Whether the payload is for a PUT request. Defaults to POST request
    :param notify: Whether articles should notify section subscribers on creation
    :return: Abridged article dict
    """
    if put:
        package = {
            'title': article['title'],
            'body': article['body'],
            'draft': article['draft'],
        }
        return {'translation': package}
    else:
        package = {
            'title': article['title'],
            'author_id': article['author_id'],
            'body': article['body'],
            'comments_disabled': article['comments_disabled'],
            'label_names': article['label_names'],
            'draft': article['draft'],
            'promoted': article['promoted'],
            'position': article['position'],
            'user_segment_id': article['user_segment_id'],
            'permission_group_id': article['permission_group_id']
        }
        return {'article': package, 'notify_subscribers': notify}


def package_comment(comment, put=False):
    """
    Creates the payload for a PUT or POST comment request.
    :param comment: Complete comment dict from API
    :param put: Whether the payload is for a PUT request. Defaults to POST request
    :return: Abridged comment dict
    """
    if put:
        package = {
            'body': comment['body']
        }
    else:
        package = {
            'author_id': comment['author_id'],
            'body': comment['body'],
            'locale': comment['locale'],
            'created_at': comment['created_at']
        }
    return {'comment': package, 'notify_subscribers': False}


def package_translation(data):
    """
    Creates the payload for a POST translation request.
    :param data: Complete translation dict from API
    :return: Abridged translation dict
    """
    package = {
        'locale': data['locale'],
        'title': data['title'],
        'body': data['body'],
        'draft': data['draft'],
    }
    return {'translation': package}


def verify_author(author_id, team_author_id, dst_kb, cross_instance=False):
    """
    Checks to see if article's author is an end user, who can't publish to HC. If yes, replace with the generic
    Zendesk team user set in settings.ini.
    :param author_id: The author's id
    :param team_author_id: The user id of a generic agent in Zendesk
    :param dst_kb: The subdomain of the destination HC
    :return: The id of an author who is not an end user
    """
    if cross_instance:
        return int(team_author_id) 
    url = 'https://{}.zendesk.com/api/v2/users/{}.json'.format(dst_kb,author_id)
    user = api.get_resource(url)   
    if user is False:
        exit()
    role = user['role']
    if role == 'end-user':
        return int(team_author_id)
    else:
        return author_id


def write_js_redirects(article_map):
    """
    The js_redirects.txt file is used in the script.js file for article redirects after migrating
    :param article_map: Dict of old:new article ids
    :return: None
    """
    file_path = os.path.join('data', 'js_redirects.txt')
    counter = 1
    with open(file_path, mode='w') as f:
        for article in article_map:
            if counter == len(article_map):
                f.write('    {}:{}\n'.format(article, article_map[article]))
            else:
                f.write('    {}:{},\n'.format(article, article_map[article]))

    return None
