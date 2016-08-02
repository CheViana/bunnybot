import time
import requests
from slackclient import SlackClient
from lxml import html
from datetime import datetime
from random import randint, choice
from decouple import config


FEEDS = {
    'bunny': 'http://dailybunny.org/feed/',
    'otter': 'http://dailyotter.org/feed/'
}

# list of env vars that should be defined:

# BOT_ID
# SLACK_BOT_TOKEN
# BOT_NAME
#


# bot's ID as an environment variable
BOT_ID = config('BOT_ID')

# bot name as env var
BOT_NAME = config('BOT_NAME')

# constants
AT_BOT = '<@' + BOT_ID + '>:'

slack_client = SlackClient(config('SLACK_BOT_TOKEN'))


def post_latest_item():
    api_call = slack_client.api_call('channels.list')
    if api_call.get('ok'):

        bunny_or_otter = 'bunny' if choice([True, False]) else 'otter'
        msg = latest_rss_item(FEEDS[bunny_or_otter])
        print('composed random {} msg'.format(bunny_or_otter))

        channels = api_call.get('channels')
        print('received channels list')
        joined_channels = [ch for ch in channels if ch.get('is_member')]

        for chat in joined_channels:
            print('posting to {}'.format(chat.get('name')))
            slack_client.api_call('chat.postMessage', channel=chat.get('id'),
                                  text=msg, as_user=True)


def handle_command(command, channel):
    '''
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    '''
    response = 'Not sure what you mean. Supported animals: otter and bunny.'
    command_found = False
    for key in FEEDS.keys():
        if key in command:
            command_found = True
            print('command ' + key)
            response = random_rss_item(FEEDS[key])
            slack_client.api_call('chat.postMessage', channel=channel, text=response, as_user=True)
    if not command_found:
        slack_client.api_call('chat.postMessage', channel=channel, text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    '''
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    '''
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


def feed(feed_url):
    xml_feed_page = requests.get(feed_url)
    xml_feed = xml_feed_page.content
    doc = html.fromstring(xml_feed)
    return doc


def msg_from_item(item):
    title = item.find('title').text

    # just find img?
    image_src = item.find('encoded').find('img').get('src')
    return '{} {}'.format(title, image_src)


def latest_rss_item(feed_url):
    doc = feed(feed_url)
    latest_item = doc.find('channel/item')
    return msg_from_item(latest_item)


def random_rss_item(feed_url):
    doc = feed(feed_url)
    items = doc.findall('channel/item')
    random_index = randint(0, len(items) - 1)
    random_item = items[random_index]
    return msg_from_item(random_item)


if __name__ == '__main__':
    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print('{} connected and running!'.format(BOT_NAME))
        posted_today = False
        post_time = (12, 0)
        reset_time = (11, 50)

        while True:
            # handle command
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)

            # at noon each day post a bunny
            timestamp = datetime.now().time()

            if not posted_today and (timestamp.hour, timestamp.minute) == post_time:
                print('time for daily post!')
                post_latest_item()
                posted_today = True

            if posted_today and (timestamp.hour, timestamp.minute) == reset_time:
                posted_today = False

            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print('Connection failed. Invalid Slack token or bot ID?')
