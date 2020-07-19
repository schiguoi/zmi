import configparser

"""
Returns a credentials tuple
:param kb: The destination kb from the settings.ini file
:return: a credentials tuple including a username and token.
"""
def get_auth(kb=None):
    config = configparser.ConfigParser()
    config.read('auth.ini')
    src = config['SRC']
    dst = config['DST']
    
    if kb == dst['kb']:
        return '{}/token'.format(dst['username']), dst['token']
    else:
        return '{}/token'.format(src['username']), src['token']
