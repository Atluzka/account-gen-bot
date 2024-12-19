# Account Generator Bot
### THIS PROGRAM DOES NOT MAKE ACCOUNTS FOR YOU.
A discord bot which manages a database of accounts and provides a user-friendly way to retrive them. Users can generate them thru an command and receive the account in their DMs. The bot ensures that each account is only distributed once, keeping the process organized and efficient.

# Commands
Parameters marked with a star(*) are required.
* `/addstock *[service] *[txt_file] [is_premium] [is_silent]` - Adds your lines to the database.
* `/blacklist *[user] [status]` - Blacklist the user from using /gen.
* `/bulkgen *[service] *[amount] *[is_premium] [is_silent]` - Admin only. Generate multiple accounts at a time.
* `/clearservice *[service] [is_premium]` - Clear all lines from a specific stock.
* `/cooldown reset *[user] [stage]` - Resets their current cooldown. (not custom cooldown)
* `/cooldown set *[user] *[stage] [time_sec] [is_silent]` - Sets a custom cooldown for the user.
* `/gen *[service] [is_premium]` - Gets a random line from the database and sends it to the user.
* `/setnote *[user] *[note]` - Set a custom note for the user, u can see it when doing /user [user]
* `/stock` - See, how many lines are in the database.
* `/subscription add *[user] *[time_sec] [is_silent]` - Admin only. Add time to user's subscription.
* `/subscription massadd *[time_sec] [is_silent]` - Admin only. Extend everyones subscription. (only people who had a sub)
* `/subscription remove *[user] [is_silent]` - Admin only. Remove users subscription.
* `/subscription set *[user] *[time_sec] [is_silent]` - Admin only. Set users premium subscription.
* `/subscription view [user] [is_silent]` - View your(user only) or other people's(admin only) subscription.
* `/user *[user]` - Admin only. View info about user.


# How to setup
Having problems setting it up? You can contact me in discord. If I'm free I can help you with setup.

(This tutorial might be missing some stuff, if i forgot something)
### 1. INSTALLING PYTHON (dont skip)
First of all make sure you have python installed (3.11.6 recommended) on the machine you want to host the bot on. (Yes, you have to host the bot yourself. There is **NO** invite link.).
When installing python, make sure to enabled 'ADD TO PATH' in the installer. If you have multiple versions of python installed, uninstall all of them and install 3.11.6 from [PYTHON](https://www.python.org/downloads/release/python-3116/)

### 2. DOWNLOADING THE SOURCE
Download all the files in the github. **DO NOT** edit any of the .py files (if you don't know what you're doing). Everything you want/need to edit is inside the config.json file.

### 3. INSTALLING THE MODULES. (!)
Open an console in the directory where the source is at and run the command: `pip install -r requirements.txt`

### 4. CONFIG (!)
In the config you need to put your **DISCORD BOT TOKEN** not your account token, which u can get from the [Discord Developer Portal](https://discord.com/developers/docs/). You make the bot and then go to the **BOT** tab and click on reset token, it will ask for password or code if you have mfa on your discord account. After confirming, copy the token and put it in your config. To get the guild-id aka your server id you need to enable developer mode in discord and right clicking on your server icon -> copy server id. Fill out the gen-channels, premium-gen-channels, admin-roles and the roles. You can also edit the footer message and the dm message in the config.

### 5. INVITING THE BOT
You can invite it from the Discord Developer Portal. Choose the bot you want to invite. Go to OAuth2 tab. Scroll down to 'OAuth2 URL Generator'. Enable 'bot' and 'applications.commands'. An invite link gets generated at the bottom. Copy it and open it in a new tab.
Invite the bot to your server. Now you can run the main.py file.


# Errors

If you get any errors that are not listed here feel free to contact me in discord, you can get my discord from my github profile.

### 1. Privileges/intents
Go to https://discord.dev and enable all the intents for your application. (discord.dev -> applications -> choose your application -> bot -> scroll down a bit -> there should be 'Privileged Gateway Intents' -> enable all)

### 2. Not sending messages
Make sure your intents are enabled and the bot has permission to send messages in the channel you're using the bot in. (You also have to specify the channels where the generate command can be used in thru the config). If the bot doesn't send a DM then make sure your dms are open.

### 4. Addstock doesn't work
It takes each line as an account from the txt file, so each account has to be on a seperate line.

Example of an txt file (it can be any of those):
```
account@gmail.com:test
tester:hello|capture
or just a piece of text
```
