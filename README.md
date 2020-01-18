<h1 align=center>XKCD Bot</h1>
<p align=center>A bot for /r/xkcd that posts detailed comments about xkcd comics</p>

## About The Project

After seeing [this suggestion](https://www.reddit.com/r/xkcd/comments/epmpwv/why_do_we_not_have_a_bot/) on the /r/xkcd subreddit, I began working on this bot. It is intended to be a non-intrusive bot that provides a detailed and well formatted comment with information regarding the relevant comic. 

It is currently running 24/7 in the cloud. You can find the bot at [/r/BobbyTablesBot](https://www.reddit.com/user/BobbyTablesBot/).
## Example
To use the bot, all you have to do is type the number of the xkcd comic you would like to link in the comment section of any post in /r/xkcd. It is quite conservative with it's matching pattern in order to avoid triggering false positives.

For example, if a comment was submitted saying:

> Show me 327  

The bot would respond with:

> **[327:](http://xkcd.com/327)** Exploits of a Mom    
> **Alt-text:** Her daughter is named Help I'm trapped in a driver's license factory.  
> [Image](https://imgs.xkcd.com/comics/exploits_of_a_mom.png)  
> [Mobile](http://m.xkcd.com/327)  
> [Explanation](http://www.explainxkcd.com/wiki/index.php/327)  
> ---
> ^[xkcd.com](https://www.xkcd.com)&nbsp;|&nbsp;[Feedback](https://reddit.com/message/compose/?to=banana_shavings&subject=BobbyTablesBot)&nbsp;|&nbsp;[Stop&nbsp;Replying](https://reddit.com/message/compose/?to=BobbyTablesBot&subject=Ignore%20Me&message=Ignore%20Me)&nbsp;|&nbsp;[GitHub](https://github.com/joeyvanlierop/xkcdbot)&nbsp;|&nbsp;[Programmer](https://www.reddit.com/user/banana_shavings)


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
