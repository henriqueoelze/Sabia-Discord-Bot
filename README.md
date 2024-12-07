
# Sabiá Bot
<img src="https://github.com/henriqueoelze/Sabia-Discord-Bot/blob/main/res/images/icon.png" alt="drawing" width="200"/>

This is a simple discord bot that allow you to listen to another discord servers to your discord forum threads.

As now (2024), Discord allow you to follow other announcement channels from any server, but you can ONLY listen to another text channel, not allowing you to send the messages to forum threads, which limits the usability in certain way.

This bot solves that.


## Bot Commands

The bot has just a few commands:

### /print_rule
Print the whole server configuration

### /set_announce_channel
Set the channel where your server is listening to the other servers messages

It was a design choice to allow just one channel for now. The idea is that your server centralize all the followed channels in a single place, and them the bot could proxy them.

### /add_rule
Add the routing rule from your configuration given the webhook id

### /remove_rule
Remove the routing rule from your configuration given the webhook id.

## How to use it

First of all, invite your bot to your channel using this link: https://discord.com/oauth2/authorize?client_id=1310691560400224256

Once you could call the commands, start with the `/set_announce_channel`, and pass the channel from your server that will receive all the other servers messages.

After that, call `/print_config`.
At this point, it will list all your integrations, with ID and name. All of them won't have any configuration at this point.

From there, call `/add_rule` for any notifications you want to create. If will require the webhook id (already listed from the `/print_configs`) and your thread (just need to type or select from the list).

Once you configured all that you want, just call `/print_config` again to make sure everything is in place.
## Stack

**Discord integration:** Pycord

**Database:** Postgress


## Author
- [@henriqueoelze](https://www.github.com/henriqueoelze)



# Contributing

If you want to contribute to the project, feel free to open issues and merge requests.

I will try to keep my eye in the repo as maximum as possible, but it is important to say that it was created using my free time, and I will continue to check it using it, so expect some hours before I could answer the questions and review the code.




## Licença

[MIT](https://choosealicense.com/licenses/mit/)

