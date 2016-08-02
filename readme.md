## Bunnybot script
Bot for Slack that posts pic from one of rss feeds each day at noon.
Also posts random pic from specific feed for mentioning bot & feed name.
Example:

    if BOT_NAME=bunnybot and you post:
    @bunnybot: gimme a bunny pic

    @bunnybot will post a bunny pic


Build using this [manual](https://www.fullstackpython.com/blog/build-first-slack-bot-python.html).

### List of env vars that should be defined:

- BOT_ID: str
- SLACK_BOT_TOKEN: str
- BOT_NAME: str
- FEEDS: json with dict[str, str], where key is feed name and value is feed url. Example: {"bunny": "http://dailybunny.org/feed/", "otter": "http://dailyotter.org/feed/"}.