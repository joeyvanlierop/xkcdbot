<h1 align=center>XKCD Bot</h1>
<p align=center>A bot for /r/xkcd that replies to any comment referencing a valid xkcd comic number with a detailed reply</p>

## About The Project

After seeing [this suggestion](https://www.reddit.com/r/xkcd/comments/epmpwv/why_do_we_not_have_a_bot/) on the /r/xkcd subreddit, I began working on this bot. It is intended to be a non-intrusive bot that provides a detailed and well formatted comment with information regarding the relevant comic. 

It is currently running 24/7 in the cloud. You can find the bot at [/r/BobbyTablesBot](https://www.reddit.com/user/BobbyTablesBot/).

## Getting Started

To host your own xkcd bot, follow these simple example steps.
    

### Prerequisites

* Python3
* A Reddit Account
  

### Installation


* Clone the repo

      git clone git@github.com:joeyvanlierop/xkcdbot.git
    
* Create an app [here](https://www.reddit.com/prefs/apps)
   * Create a copy of [config.examply.py](bot/config.example.py)
   * Paste the appropritate credentials into the newly created config.py
   * Make sure to also add an appropriate user agent in the config.py
* Install the requirements

      pip3 install -r requirements.txt

### Running the bot

    python3 bot.py
    
### Start automatically at reboot

To start the bot automatically in the background on Linux, add a cronjob with

    crontab -e
   
and add this line (replace <path> with path to your local repository)

    @reboot python3 <path>/bot.py &>> /dev/null

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
