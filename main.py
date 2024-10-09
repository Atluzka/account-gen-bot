import discord, json, sqlite3
from datetime import datetime, timedelta
from discord import app_commands
from typing import List
from io import StringIO

from src import database
from src import utils
from src import cooldown_manager

# connect to the database
con = sqlite3.connect('accounts.db'); con.row_factory = sqlite3.Row

# discord bot stuff
bot = discord.Client(intents=discord.Intents.default())
tree = app_commands.CommandTree(bot)
config = json.load(open('config.json'))

serviceList = []
is_everything_ready = False 

async def updateServices():
    global serviceList
    serviceList = await database.getServices(con)
    return

user_cooldowns = []

@bot.event
async def on_ready():
    global is_everything_ready
    await tree.sync(guild=discord.Object(id=config["guild-id"]))
    
    await updateServices()
    print("Servicelist:", serviceList)
    
    is_everything_ready = True
    print("Logged in as {0.user}".format(bot))

async def service_autcom(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    types = serviceList
    return [
        app_commands.Choice(name=service, value=service)
        for service in types if current.lower() in service.lower()
    ]

@tree.command(name = "deleteservice", description = "(admin only)", guild=discord.Object(id=config["guild-id"]))
@app_commands.autocomplete(service=service_autcom)
async def deleteservice(interaction: discord.Interaction, service: str):
    
    if not interaction.user.id in config['admins']:
        return await interaction.response.send_message(str(config['messages']['noperms']), ephemeral=True)
    
    if not is_everything_ready:
        return await interaction.response.send_message("Bot is starting.", ephemeral=True)

    db_res1 = await database.deleteService(con, service, serviceList)
    if db_res1:
        await updateServices()

    embd=discord.Embed(
        title=f"Delete Service",
        description=f'{"Successfully deleted service" if db_res1 else "Error. Service doesnt exist."}',
        color=int(config['colors']['success']) if db_res1 else int(config['colors']['error'])
    )
    embd.set_footer(text=config['messages']['footer-msg'])
    
    return await interaction.response.send_message(embed=embd, ephemeral=True)

@tree.command(name = "bulkgen", description = "Generate multiple accounts of your choice", guild=discord.Object(id=config["guild-id"]))
@app_commands.autocomplete(service=service_autcom)
async def bulkgen(interaction: discord.Interaction, service: str, amount: int):
    global user_cooldowns
    
    if not is_everything_ready:
        return await interaction.response.send_message("Bot is starting.", ephemeral=True)
    
    if service not in serviceList:
        return await interaction.response.send_message(f'Invalid service.', ephemeral=True)

    is_admin = interaction.user.id in config['admins']

    if not is_admin and not interaction.channel_id in config["gen-channels"]:
        channel_list = [f"<#{channel}>" for channel in config["gen-channels"]]
        return await interaction.response.send_message(str(config['messages']['wrongchannel']) + ', '.join(channel_list), ephemeral=True)

    utl_res, canbulkgen, max_gen_amnt = await utils.does_user_meet_requirements(interaction.user.roles, config, service, isbulkgen=True)
    if not is_admin:
        if not canbulkgen:
            return await interaction.response.send_message(str(config['messages']['noperms']), ephemeral=True)
        
        if max_gen_amnt < amount:
            return await interaction.response.send_message(f"You can't generate more than {max_gen_amnt} accounts per bulkgen.", ephemeral=True)
        
        if not utl_res:
            return await interaction.response.send_message(str(config['messages']['noperms']), ephemeral=True)

    # Cooldown
    _user_cldw = None
    has_cldw = await cooldown_manager.does_user_have_cooldown(user_cooldowns, interaction.user.id)
    if interaction.user.id not in config['admins'] and not has_cldw:
        _user_cldw = await cooldown_manager.get_role_user_cooldown(interaction)
        if _user_cldw is not None:
            user_cooldowns.append(f"{interaction.user.id}:{int(_user_cldw)}")
    elif has_cldw:
        _data = await cooldown_manager.getCooldownData(user_cooldowns, interaction.user.id)
        if _data['stillHasCooldown']:
            embd=discord.Embed(title="Cooldown",description=f':no_entry_sign: {_data["formatedCooldownMsg"]}',color=config['colors']['error'])
            return await interaction.response.send_message(embed=embd, ephemeral=False)
        elif _data['secondsTillEnd'] == 0:
            user_cooldowns.remove(f"{interaction.user.id}:{int(_data['endTime'])}")
            _user_cldw = await cooldown_manager.get_role_user_cooldown(interaction)
            if _user_cldw is not None:
                user_cooldowns.append(f"{interaction.user.id}:{int(_user_cldw)}")

    success, accounts, account_left = await database.getMultipleAccounts(con, service, amount)
    if not success:
        if _user_cldw:
            user_cooldowns.remove(f"{interaction.user.id}:{int(_user_cldw)}")
        return await interaction.response.send_message(f"There is no stock left (´{account_left}´ accounts left).", ephemeral=True)
    else:
        
        channel = await interaction.user.create_dm()
        embd=discord.Embed(
            title=f"Account Generated :label: ",
            description=config['messages']['altsent'],
            color=config['colors']['success']
        )
        embd.set_footer(text=config['messages']['footer-msg'],icon_url=interaction.user.avatar.url)

        embd2=discord.Embed(title=f"`{service}` generated :label: ",description=':incoming_envelope: Check your DMs for the account.',color=config['colors']['success'])
        embd2.set_footer(text=config['messages']['footer-msg'],icon_url=interaction.user.avatar.url)
        embd2.set_image(url=config["generate-settings"]["gif-img-url"])
        await channel.send(embed=embd, file=discord.File(fp=StringIO("\n".join([str(account) for account in accounts])), filename=f'{service}.txt'))
        return await interaction.response.send_message(embed=embd2, ephemeral=False)

@tree.command(name = "gen", description = "Generate an account of your choice", guild=discord.Object(id=config["guild-id"]))
@app_commands.autocomplete(service=service_autcom)
async def gen(interaction: discord.Interaction, service: str):
    global user_cooldowns
    
    if not is_everything_ready:
        return await interaction.response.send_message("Bot is starting.", ephemeral=True)
    
    if service not in serviceList:
        return await interaction.response.send_message(f'Invalid service.', ephemeral=True)

    if not interaction.user.id in config['admins'] and not interaction.channel_id in config["gen-channels"]:
        channel_list = [f"<#{channel}>" for channel in config["gen-channels"]]
        return await interaction.response.send_message(str(config['messages']['wrongchannel']) + ', '.join(channel_list), ephemeral=True)

    utl_res = await utils.does_user_meet_requirements(interaction.user.roles, config, service)
    if not interaction.user.id in config['admins'] and not utl_res:
        return await interaction.response.send_message(str(config['messages']['noperms']), ephemeral=True)

    # Cooldown
    _user_cldw = None
    has_cldw = await cooldown_manager.does_user_have_cooldown(user_cooldowns, interaction.user.id)
    if interaction.user.id not in config['admins'] and not has_cldw:
        _user_cldw = await cooldown_manager.get_role_user_cooldown(interaction)
        if _user_cldw is not None:
            user_cooldowns.append(f"{interaction.user.id}:{int(_user_cldw)}")
    elif has_cldw:
        _data = await cooldown_manager.getCooldownData(user_cooldowns, interaction.user.id)
        if _data['stillHasCooldown']:
            embd=discord.Embed(title="Cooldown",description=f':no_entry_sign: {_data["formatedCooldownMsg"]}',color=config['colors']['error'])
            return await interaction.response.send_message(embed=embd, ephemeral=False)
        elif _data['secondsTillEnd'] == 0:
            user_cooldowns.remove(f"{interaction.user.id}:{int(_data['endTime'])}")
            _user_cldw = await cooldown_manager.get_role_user_cooldown(interaction)
            if _user_cldw is not None:
                user_cooldowns.append(f"{interaction.user.id}:{int(_user_cldw)}")

    success, account = await database.getAccount(con, service)
    if not success:
        if _user_cldw:
            user_cooldowns.remove(f"{interaction.user.id}:{int(_user_cldw)}")
        return await interaction.response.send_message(f"There is no stock left.", ephemeral=True)
    else:
        
        channel = await interaction.user.create_dm()
        embd=discord.Embed(
            title=f"Account Generated :label: ",
            description=config['messages']['altsent'] + f"\n```{account['combo']}```",
            color=config['colors']['success']
        )
        embd.set_footer(text=config['messages']['footer-msg'],icon_url=interaction.user.avatar.url)

        embd2=discord.Embed(title=f"`{service}` generated :label: ",description=':incoming_envelope: Check your DMs for the account.',color=config['colors']['success'])
        embd2.set_footer(text=config['messages']['footer-msg'],icon_url=interaction.user.avatar.url)
        embd2.set_image(url=config["generate-settings"]["gif-img-url"])

        await channel.send(embed=embd)
        return await interaction.response.send_message(embed=embd2, ephemeral=False)

@tree.command(name = "addstock", description = "Add stock to database (admin only)", guild=discord.Object(id=config["guild-id"]))
@app_commands.autocomplete(service=service_autcom)
async def addaccounts(interaction: discord.Interaction, service: str, file: discord.Attachment):
    
    if not interaction.user.id in config['admins']:
        return await interaction.response.send_message(str(config['messages']['noperms']), ephemeral=True)

    if not is_everything_ready:
        return await interaction.response.send_message("Bot is starting.", ephemeral=True)
    
    if service not in serviceList:
        return await interaction.response.send_message(f'Invalid service.', ephemeral=True)
    
    try:
        if not str(file.filename).endswith(".txt"):
            return await interaction.response.send_message(f'You can only upload files with .txt extension', ephemeral=True)
    except:
        return await interaction.response.send_message(f'Error when checking file.', ephemeral=True)

    if file.size > config["maximum-file-size"]:
        return await interaction.response.send_message(f'Maximum file size: `{config["maximum-file-size"]} bytes`', ephemeral=True)
    content = await file.read()

    filtered_stock = []
    dec_cont = content.decode('utf-8')
    content = str(dec_cont).split("\n")
    for item in content:
        if len(item) > 2:
            filtered_stock.append(item)
    add_cnt,dupe_cnt = await database.addStock(con, service, filtered_stock, config['remove-capture-from-stock'])
    return await interaction.response.send_message(f'`{add_cnt}` accounts have been added to the `{service}` database. `{dupe_cnt}` dupes found.', ephemeral=True)

@tree.command(name = "createservice", description = "(admin only)", guild=discord.Object(id=config["guild-id"]))
async def createservice(interaction: discord.Interaction, servicename: str):
    
    if not interaction.user.id in config['admins']:
        return await interaction.response.send_message(str(config['messages']['noperms']), ephemeral=True)
    
    if not is_everything_ready:
        return await interaction.response.send_message("Bot is starting.", ephemeral=True)

    db_res1 = await database.createService(con, servicename, serviceList)
    if db_res1:
        await updateServices()

    embd=discord.Embed(
        title=f"Create Service",
        description=f'{"Successfully created service" if db_res1 else "Error. Service already exists."}',
        color=int(config['colors']['success']) if db_res1 else int(config['colors']['error'])
    )
    embd.set_footer(text=config['messages']['footer-msg'])
    
    return await interaction.response.send_message(embed=embd, ephemeral=True)

@tree.command(name = "stock", description = "Get the amount of stock", guild=discord.Object(id=config["guild-id"]))
async def stock(interaction: discord.Interaction):
    
    if not is_everything_ready:
        return await interaction.response.send_message("Bot is starting.", ephemeral=True)
    
    stock = await database.getStock(con, serviceList)
    if len(stock) <= 0:
        embd=discord.Embed(
            title=f"Stock - 0 services",
            description='There are no services to display',
            color=config['colors']['stock'])
        embd.set_footer(text=config['messages']['footer-msg'])
        return await interaction.response.send_message(embed=embd)

    filtered_stock = [] 
    for stk in stock:
        stk = (stk.split(':'))
        filtered_stock.append(f"**{stk[0]}**: `{stk[1]}`")

    embd=discord.Embed(
        title=f"Stock - {len(filtered_stock)}",
        description='\n'.join(filtered_stock),
        color=config['colors']['stock']
    )
    embd.set_footer(text=config['messages']['footer-msg'])
    
    return await interaction.response.send_message(embed=embd, ephemeral=config['stock-command-silent'])

bot.run(config['token'])