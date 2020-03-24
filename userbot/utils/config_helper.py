import configparser
import os
from distutils.util import strtobool


sample_config_file = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'sample_config.ini'
)


def resolve_env(config: configparser.ConfigParser):
    """Check the environment variables and add them a configparser obj"""
    api_id = os.getenv('api_id', None)
    api_hash = os.getenv('api_hash', None)
    redis_endpoint = os.getenv('redis_endpoint', None)
    redis_password = os.getenv('redis_password', None)

    if "telethon" in config.sections() and not api_id and not api_hash:
        api_id = config['telethon'].get('api_id', False)
        api_hash = config['telethon'].get('api_hash', False)

    if not api_id or not api_hash:
        raise ValueError('You need to set your API Keys at least.')

    sample_config = configparser.ConfigParser()
    sample_config.read(sample_config_file)
    for section in sample_config.sections():
        if section not in config:
            config[section] = {}

    config['telethon']['api_id'] = api_id
    config['telethon']['api_hash'] = api_hash
    if redis_endpoint:
        config['telethon']['redis_endpoint'] = redis_endpoint
    if redis_password:
        config['telethon']['redis_password'] = redis_password

    userbot = {
        'userbot_regexninja': strtobool(
            os.getenv('userbot_regexninja', 'False')
        ),
        'self_destruct_msg': strtobool(
            os.getenv('self_destruct_msg', 'True')
        ),
        'pm_permit': strtobool(os.getenv('pm_permit', 'False')),
        'console_logger_level': os.getenv('console_logger_level', None),
        'logger_group_id': int(os.getenv('logger_group_id', 0)),
        'userbot_prefix': os.getenv('userbot_prefix', None),
        'default_sticker_pack': os.getenv('default_sticker_pack', None),
        'default_animated_sticker_pack': os.getenv(
            'default_animated_sticker_pack', None
        )
    }

    api_keys = {
        'api_key_heroku': os.getenv(
            'api_key_heroku', None
        ),
        'api_key_removebg': os.getenv(
            'api_key_removebg', None
        )
    }

    plugins = {
        'repos': os.getenv(
            'repos', None
        ),
        'user': os.getenv(
            'user', None
        ),
        'token': os.getenv(
            'token', None
        )
    }

    make_config(config, 'userbot', userbot)
    make_config(config, 'api_keys', api_keys)
    make_config(config, 'plugins', plugins)


def make_config(
    config: configparser.ConfigParser,
    section: str, section_dict: dict
) -> None:
    UNACCETPABLE = ['', '0', 'None', 'none', 0, None]
    for key, value in section_dict.items():
        if value is not None and value not in UNACCETPABLE:
            config[section][key] = str(value)
