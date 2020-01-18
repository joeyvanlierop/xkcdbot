<h1 align=center>XKCD Bot</h1>
<p align=center>A bot for /r/xkcd that replies to any comment referencing a valid xkcd comic number with a detailed reply</p>

## About The Project

After seeing [this suggestion](https://www.reddit.com/r/xkcd/comments/epmpwv/why_do_we_not_have_a_bot/) on the /r/xkcd subreddit, I began working on this bot. It is intended to be a non-intrusive bot that provides a detailed and well formatted comment with information regarding the relevant comic. 

It is currently running 24/7 in the cloud. You can find the bot at [/r/BobbyTablesBot](https://www.reddit.com/user/BobbyTablesBot/).
## Example
GitHub-flavored markdown slightly differs from reddit-flavored markdown, so keep in mind that the example here will not reflect the exact formatting:


**[1813:](http://xkcd.com/1813)** Vomiting Emoji  
**Alt-text:** My favorite might be U+1F609 U+1F93F WINKING FACE VOMITING.
[Image](https://imgs.xkcd.com/comics/vomiting_emoji.png)  
[Mobile](http://m.xkcd.com/1813)  
[Explanation](http://www.explainxkcd.com/wiki/index.php/1813)
---
[xkcd.com](https://www.xkcd.com)&nbsp;|&nbsp;[Bugs&nbsp;or&nbsp;Feedback](https://reddit.com/message/compose/?to=banana_shavings&subject=BobbyTablesBot)&nbsp;|&nbsp;[Stop&nbsp;Replying](https://reddit.com/message/compose/?to=BobbyTablesBot&subject=Ignore%20Me&message=Ignore%20Me)&nbsp;|&nbsp;[GitHub](https://github.com/joeyvanlierop/xkcdbot)&nbsp;|&nbsp;[Bot&nbsp;by&nbsp;/u/banana_shavings](https://www.reddit.com/user/banana_shavings)


## Getting Started

To host your own xkcd bot, follow these simple example steps.
    

### Prerequisites

* Python3
* A Reddit Account
  

### Installation


* Clone the repo

      git clone git@github.com:joeyvanlierop/xkcdbot.git
    
* Create an app [here](https://www.reddit.com/prefs/apps)
   * Create a copy of [config.example.json](xkcdbot/config.example.json) and rename it to config.json
   * Paste the appropritate credentials into the newly created config.py
   * Make sure to also add an appropriate user agent in the config.py
* Install the requirements

      pip3 install -r requirements.txt

### Running the bot

* Navigate to boy.py and run:

        python3 bot.py
    
### Start automatically at reboot

To start the bot automatically in the background on Linux, add a cronjob with

    crontab -e
   
and add this line (replace <path> with path to your local repository)

    @reboot python3 <path>/bot.py &>> /dev/null

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

* Task list:
    - [ ] Blacklisting users through inbox messages
    - [ ] Implement databases for blacklisted users and statistics
    - [ ] Match submissions (currently only matches comments)
    - [ ] Respond to mentions regardless of subreddit

## License
[MIT](https://choosealicense.com/licenses/mit/)
