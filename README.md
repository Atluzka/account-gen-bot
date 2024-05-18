<h1 align="center">
	  DISCORD GENERATOR BOT
</h1>

<h3 align="center">
	  INFO
</h3>

It uses a database to store the accounts, which people can generate. The bot has many customization options which can be changed in config.json (will make it even more customizable in next upd). It supports cookies or user/mail : pass.

This bot DOES NOT make accounts for you, you need to have the accounts yourself and u can put them inside the database which other people can generate.

I haven't made logs yet but i will add it when i feel like updating it.

<h3 align="center">
	  FEATURES

</h3>

* `/stock` - Shows stock. [Example message](https://github.com/Atluzka/account-gen-bot/assets/52002842/1b33211d-92a7-4b12-bed0-e0d49a38cdbd)
* `/generate [service]` - Will get an account/cookie from the database and send it to the user. [server message](https://github.com/Atluzka/account-gen-bot/assets/52002842/87d7ddb4-efbe-4b96-8e29-bc42e57e1d5e), [DMs message](https://github.com/Atluzka/account-gen-bot/assets/52002842/bfc7d186-5e71-42bd-a002-756640485abb)
* `/addstock [service] [upload file]` - Will add stock to database. Also checks for dupes. [Before running](https://github.com/Atluzka/account-gen-bot/assets/52002842/d9dea2fd-2e25-4bde-bace-e538da0118b0), [After running](https://github.com/Atluzka/account-gen-bot/assets/52002842/91764c4c-2ae5-4fab-9aff-6f3e37044e0b)
* `/createservice [name] [type]` - Creates a service in the database. [example](https://github.com/Atluzka/account-gen-bot/assets/52002842/77bfa2a1-23d3-401a-9a17-bda33724751d)
* `/deleteservice [service]` - Will ask for confirmation. [confirmation example](https://github.com/Atluzka/account-gen-bot/assets/52002842/771fb803-2388-487f-a8a8-6ea8c4a7312e)
* Highly customizable.
* Easy to use and lightweight.

<h3 align="center">
	  ERRORS

</h3>

Make sure you have everything installed. Put this inside a `requirements.txt` file
```
discord.py==2.3.2
typing==3.7.4.3
datetime==5.2
```
Open a console in the folder u made the file in and run this:
```
pip install -r requirements.txt
```

Exmaple of a txt file (for addstock command)
```
username:password
email:password
```

If you get an error related to Privileges/intents go to [discord.dev](https://discord.dev) and enable all the intents for your application. 
(discord.dev -> applications -> choose your application -> bot -> scroll down a bit -> there should be 'Privileged Gateway Intents' -> enable all)

The bot is not sending any messages? Make sure your intents are enabled and the bot has permission to send messages in the channel you're using the bot in. (You also have to specify the channels where the generate command can be used in.)

You dont get a dm from the bot? Make sure your dms are open.

If you have any other errors make a issue about it or you can also message me in discord (you can find my discord on my profile.)
