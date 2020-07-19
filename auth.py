import configparser

"""
Returns a credentials tuple
:param kb: The auth configuration
:return: a credentials tuple including a username and token.
"""
def get_auth(kb=src['kb']):
    config = configparser.ConfigParser()
    config.read('auth.ini')
    src = config['SRC']
    dst = config['DST']
    
    if kb == src['kb']:
        return '{}/token'.format(src['username']), src['token']
    elif kb == dst['kb']:
        return '{}/token'.format(dst['username']), dst['token']
