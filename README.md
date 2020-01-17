# XKCD Bot

This is a reddit bot written in Python using [PRAW](https://github.com/praw-dev/praw). It is designed to reply to comments posted in /r/xkcd with a formatted response referencing any numbers which correlate to a valid xkcd comic.

## Installation

`git clone` the repository, or `Download ZIP` and unzip.

## Usage

* `cd xkcdbot/bot`
* Install all requirements with `pip install -r requirements.txt`
* Create a [reddit app](http://reddit.com/prefs/apps) as script
* Set a valid `username`, `password`, `client_id`, `client_secret`, and `user_agent` in the `bot/config.py` file
* Run the bot with `python bot.py`

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
