<h1 align="center">
	  DISCORD ACCOUNT GENERATOR BOT
</h1>

<p align="center">
	  Disclaimer: This bot doesn't generate accounts out of thin air, you need stock.
</p>

<h3 align="center">
	  INFO
</h3>

Using commands such as `/gen` (`/pgen` for premium users), people can generate accounts, codes or other similar things. 

You put bunch of accounts in mail:pass or user:pass format in a text file and if a user uses one of the commands mentioned before they can generate the accounts. They can also be codes like giftcards.

It takes the last line from the text file and sends it to the user (of course it deletes the line as well, so there won't be any duplicates)

<h3 align="center">
	  FEATURES
</h3>

* `/stock` - Get all of the available services and how many accounts there are.
* `/gen {name of the service}` - Generates an account and sends it to the user's DMs.
* `/pgen {name of the service}` - Same as /gen but for premium users.
* `/add {premium: true/false} {name of the service} {account to add}` - Adds an account to service. Admin only command.
* `/create {premium: true/false} {name of the service}` - Creates a service. Admin only command.
* Logs - Sends you info such as who and when did somebody generate an account also shows you the account details.
* Highly customizable. Change premium, free and admin cooldowns. Choose which channels the generate command can be used in. Switch logs on or off. If you want to change embed colors then do so in the bot.py file because json doesnt support hex i can't put them into the config.json file. Might find a way to do it but its not priority.
* Clean and customizable messages.
* Easy to use and lightweight. Works well with large amount of accounts or many people using it at once.

<h3 align="center">
	  SCREENSHOTS
</h3>
<div align="center"> 
    <img style="border-radius: 15px; display: block; margin-left: auto; margin-right: auto; margin-bottom:20px;" width="50%" src="https://github.com/Atluzka/account-gen-bot/assets/52002842/11d18764-3559-4c5b-ae20-a2d31cd3f636"></img>
    <img style="border-radius: 15px; display: block; margin-left: auto; margin-right: auto; margin-bottom:20px;" width="50%" src="https://github.com/Atluzka/account-gen-bot/assets/52002842/0004c18d-d914-4f08-8927-afd632972f64"></img>
    <img style="border-radius: 15px; display: block; margin-left: auto; margin-right: auto; margin-bottom:20px;" width="50%" src="https://github.com/Atluzka/account-gen-bot/assets/52002842/7a3c31c7-8567-4c2f-bd45-46969a805b12"></img>
</div>
