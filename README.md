<h1 align=center>XKCD Bot</h1>
<p align=center>A bot for /r/xkcd that posts detailed comments about xkcd comics</p>

## About The Project

After seeing [this suggestion](https://www.reddit.com/r/xkcd/comments/epmpwv/why_do_we_not_have_a_bot/) on the /r/xkcd subreddit, I began working on this bot. It is intended to be a non-intrusive bot that provides a detailed and well formatted comment with information regarding the relevant comic. 

It is currently running 24/7 in the cloud. You can find the bot at [/u/BobbyTablesBot](https://www.reddit.com/user/BobbyTablesBot/).
## Example
There are two ways to use the bot.

* The first way is to post a comment in /r/xkcd with the number of the xkcd comic you would like to link prefixed by an exclamation mark (!) or a pound sign (#).  
  Examples:

  > !327  

  or
  > #327 

  or even
  > Show me !327


* The second way is to mention the bot from any subreddit with the number of the xkcd comic you would like to link. If the bot is mentioned, the comic number does not need to be prefixed.  
  Examples:

    > /u/BobbyTablesBot 327  

    or
    > /u/BobbyTablesBot !327

    or even
    > Hey /u/BobbyTablesBot, can you link me 327?

In any of the previous cases, the bot would respond with:

> **[327:](http://xkcd.com/327)** Exploits of a Mom    
> **Alt-text:** Her daughter is named Help I'm trapped in a driver's license factory.  
> [Image](https://imgs.xkcd.com/comics/exploits_of_a_mom.png)  
> [Mobile](http://m.xkcd.com/327)  
> [Explanation](http://www.explainxkcd.com/wiki/index.php/327)  
> ---
> [xkcd.com](https://www.xkcd.com)&nbsp;|&nbsp;[Feedback](https://reddit.com/message/compose/?to=banana_shavings&subject=BobbyTablesBot)&nbsp;|&nbsp;[Stop&nbsp;Replying](https://reddit.com/message/compose/?to=BobbyTablesBot&subject=Ignore%20Me&message=Ignore%20Me)&nbsp;|&nbsp;[GitHub](https://github.com/joeyvanlierop/xkcdbot)&nbsp;|&nbsp;[Programmer](https://www.reddit.com/user/banana_shavings)


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

* From the base directory run:

        python3 -m bot.bot
        
### Running the tests

* From the base directory run:

        python3 -m unittest discover

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

* Task list:
    - [x] Blacklisting users through inbox messages
    - [x] Implement databases for blacklisted users and statistics
    - [x] Respond to mentions regardless of subreddit
    - [x] [Remove duplicate entries](https://www.reddit.com/r/xkcd/comments/erydbl/introducing_ubobbytablesbot/ff7k8mg/)
    - [x] [Track comic reference popularity](https://www.reddit.com/r/xkcd/comments/erydbl/introducing_ubobbytablesbot/ff75nen/)
    - [ ] Include statistics in comment
    - [ ] Implement logging
    - [ ] Match submissions (currently only matches comments)
    - [ ] [Literalize certain Markdown reserves characters when they appear as part of a URL](https://www.reddit.com/r/xkcd/comments/erydbl/introducing_ubobbytablesbot/ff6z3yz/)
    - [ ] [Return random comic](https://www.reddit.com/r/xkcd/comments/erydbl/introducing_ubobbytablesbot/ff7wmeh/)
    - [ ] [Handle range of ids](https://www.reddit.com/r/xkcd/comments/erydbl/introducing_ubobbytablesbot/ff7s6zt/)
    - [ ] [Open on explainxkcd](https://www.reddit.com/r/xkcd/comments/erydbl/introducing_ubobbytablesbot/ff81kky/)
    - [ ] [Backlog/queue script](https://www.reddit.com/r/xkcd/comments/erydbl/introducing_ubobbytablesbot/ff8gjyc/)

## License
[MIT](https://choosealicense.com/licenses/mit/)
