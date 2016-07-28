import os
from slackclient import SlackClient


BOT_NAME = 'bunnybot'

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


if __name__ == "__main__":
    api_call = slack_client.api_call("users.list")
    print('hey')
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        print('ok')
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
    else:
        print('not ok')
        print("could not find bot user with the name " + BOT_NAME)
