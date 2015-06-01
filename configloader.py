import ConfigParser

class ConfigLoader:
    """parses and assigns config to flask app"""
    def __init__(self, app):
        config = ConfigParser.RawConfigParser()
        config.read('settings.cfg')

        app.config['secret_key'] = config.get('AppSettings', 'secret_key')
        app.config['host']=config.get('AppSettings','host')
        app.config['port']=config.get('AppSettings','port')

        app.config['client_id'] = config.get('OAuthSettings', 'client_id')
        app.config['client_secret'] = config.get('OAuthSettings', 'client_secret')
        app.config['authorize_url'] = config.get('OAuthSettings', 'authorize_url')
        app.config['access_token_url'] = config.get('OAuthSettings','access_token_url')