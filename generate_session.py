import configparser
import os
import platform
import sys
import os.path


if platform.python_version_tuple() < ('3', '7', '3'):
    print(
        "Please run this script with Python 3.7.3 or above."
        "\nExiting the script."
    )
    sys.exit(1)


try:
    import telethon
except (ModuleNotFoundError, ImportError):
    cmd = f'"python -m pip install -U telethon --user"'
    print(
        f"Telethon not found! Install it using {cmd} and run the script again"
    )
    sys.exit()


redis = False

if os.path.exists('./config.ini'):
    config = configparser.ConfigParser()
    config.read('./config.ini')
    api_id = config['telethon'].getint('api_id', False)
    api_hash = config['telethon'].get('api_hash', False)
    if not (api_id or api_hash):
        print("Invalid config file! Fix it before generating a session.")
        sys.exit(1)
    redis_ip = input("Would you like to generate a Redis session? (yes/no): ")
    if redis_ip.lower() in ('y', 'yes'):
        endpoint = config['telethon'].get('redis_endpoint', False)
        password = config['telethon'].get('redis_password', False)
        if not (endpoint or password):
            print(
                "Make sure you have redis_endpoint and redis_password"
                "in your config.ini"
            )
            sys.exit(1)
        elif ':' not in endpoint:
            print("Invalid Redis endpoint.")
            sys.exit(1)
        redis = True
else:
    api_id = input("Enter your API ID: ")
    api_hash = input("Enter your API hash: ")
    redis_ip = input("Would you like to generate a Redis session? (yes/no): ")
    if redis_ip.lower() in ('y', 'yes'):
        while True:
            endpoint = input("Enter your Redis endpoint: ")
            if ':' in endpoint:
                break
            else:
                print('Invalid Redis endpoint! Try again.')
        password = input("Enter your Redis password: ")
        redis = True

if redis:
    try:
        import redis
    except (ModuleNotFoundError, ImportError):
        cmd = f'"python -m pip install -U redis --user"'
        print(
            f"Telethon not found! Install it using {cmd} and "
            "run the script again"
        )
        sys.exit()

    from userbot.utils.sessions import RedisSession

    redis_connection = redis.Redis(
        host=endpoint.split(':')[0],
        port=endpoint.split(':')[1],
        password=password.strip()
    )
    try:
        redis_connection.ping()
    except Exception:
        print("Invalid Redis credentials! Exiting the script")
        sys.exit(1)
    session = RedisSession("userbot", redis_connection)
else:
    session = "userbot"

with telethon.TelegramClient(session, api_id, api_hash) as client:
    me = client.loop.run_until_complete(client.get_me())
    name = telethon.utils.get_display_name(me)
    print(f"Successfully generated a session for {name}")
