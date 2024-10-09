# Account Generator Bot
A discord bot which manages a database of accounts and provides a user-friendly way to retrive them. Users can generate them thru an command and receive the account in their DMs. The bot ensures that each account is only distributed once, keeping the process organized and efficient.

# Commands
* `/stock` - Retrives the amount of stock left from the database.
* `/gen [service]` - Generates an account and sends it to the users DMs.
* `/bulkgen [service] [amount]` - Generates multiple accounts and sends them to the users DMs.
* `/addstock [service] [upload txt file]` - Adds stock to the desired service. Checks for dupes.
* `/createservice [service]` - Creates a service in the database.
* `/deleteservice [service]` - Deletes a service from the database.

# Config

Explanation to some things in the config.
Do not paste this inside your config, it will not work.
```json
{
    "token": "Here put your 'BOT TOKEN', NOT your 'ACCOUNT TOKEN'",
    "guild-id": "This is self-explanatory, here goes the ID of your server/guild", 
    "stock-command-silent": "boolean, makes the stock command only visible to the user who used the command."
    "remove-capture-from-stock": "boolean, will remove '| your capture here' if you have it in the stock"
    "gen-channels": "A list of all the channels where the /generate command can be used in."
    "admins": "A list of admins, you must add yourself as an admin (your discord user id) in order to use admin only commands."
    "roles": [
        {
            "id": "Id of the role",
            "cooldown": "Here put the cooldown in seconds, this is a integer.",
	    "can-bulk-gen": "boolean, switch if the user can use the bulkgen command or not. true - means they can.",
            "bulk-gen-max": "int, how many accounts can they generate per bulkgen.",
            "gen-access": [
		"Here put",
		"The names of all the services u want the user with this",
		"role to have access to."
		"You can also use 'all' if you want to give access to all the services"
	    ]
        }
    ],

    "messages": "Self-explanatory, here is the list of the messages which can be easily changed."
    "generate-settings": { "gif-img-url": "HERE GOES THE DIRECT URL OF A PICTURE/GIF THAT WILL BE SENT EVERYTIME SOMEONE GENERATES SOMETHING" },
    "maximum-file-size": "The maximum file size in bytes, default is 2mb"
}
```

# Errors

If you get any errors that are not listed here feel free to contact me in discord, you can get my discord from my github profile.

### 1. Privileges/intents
Go to https://discord.dev and enable all the intents for your application. (discord.dev -> applications -> choose your application -> bot -> scroll down a bit -> there should be 'Privileged Gateway Intents' -> enable all)

### 2. Not sending messages
Make sure your intents are enabled and the bot has permission to send messages in the channel you're using the bot in. (You also have to specify the channels where the generate command can be used in thru the config). If the bot doesn't send a DM then make sure your dms are open.

### 3. ModuleNotFound
Install the requirered modules: **discord.py**, **typing**, **datetime**. If it doesn't work after that, reinstall python completely. I recommend downloading the 3.11.6 version from https://python.org. While installing make sure "ADD TO PATH" is enabled.

### 4. Addstock doesn't work
It takes each line as an account from the txt file, so each account has to be on a seperate line.

Example of an txt file (it can be any of those):
```
account@gmail.com:test
tester:hello|capture
or just a piece of text
```
