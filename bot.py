import discord, json, os, sqlite3, requests, string, random
from discord import app_commands
from discord.ui import Button, View
from datetime import datetime, timedelta
from io import StringIO
from discord.ext import commands
from typing import List

# connect to the database
con = sqlite3.connect('accounts.db')
con.row_factory = sqlite3.Row

bot = discord.Client(intents=discord.Intents.default())
tree = app_commands.CommandTree(bot)
config = json.load(open('./bin/config.json'))

service_list = []
premium_service_list = []
cookie_service_list = []
premium_cookie_service_list = []
Abkradam = []

# yes the code looks ass, but it works.
async def getServices():
    global service_list, premium_service_list,Abkradam,cookie_service_list,premium_cookie_service_list
    premium_cookie_service_list = []
    cookie_service_list = []
    service_list = []
    premium_service_list = []
    Abkradam = []
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = cur.fetchall()
    cur.close()
    for table in table_names:
        if str(table[0]).split('_')[0] == 'paccounts':
            premium_service_list.append(str(table[0]).split('_')[1])
        elif str(table[0]).split('_')[0] == 'accounts':
            service_list.append(str(table[0]).split('_')[1])
        elif str(table[0]).split('_')[0] == 'pcookie':
            premium_cookie_service_list.append(str(table[0]).split('_')[1])
        elif str(table[0]).split('_')[0] == 'cookie':
            cookie_service_list.append(str(table[0]).split('_')[1])
    for service in service_list:
        Abkradam.append(service)
    for service in premium_service_list:
        Abkradam.append(service)
    for service in cookie_service_list:
        Abkradam.append(service)
    for service in premium_cookie_service_list:
        Abkradam.append(service)
    return

@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=config["guild-id"]))
    await getServices()
    print('Services:', Abkradam)
    print("Logged in as {0.user}".format(bot))

@bot.event
async def on_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.CommandOnCooldown):
        await interaction.response.send_message('Cooldown, {round(error.retry_after, 2)}', ephemeral=True)

async def getName(service):
    if service in service_list:
        name = f"accounts_{service}"
        iscookie = False
        ispremium = False
    elif service in premium_service_list:
        name = f"paccounts_{service}"
        iscookie = False
        ispremium = True
    elif service in cookie_service_list:
        name = f"cookie_{service}"
        iscookie = True
        ispremium = False
    elif service in premium_cookie_service_list:
        name = f"pcookie_{service}"
        iscookie = True
        ispremium = True
    return (name, iscookie, ispremium)

async def addStock(name, stock, iscookie):
    cursor = con.cursor()
    dupe_amount = 0
    already_added = []
    if iscookie:
        for cookie in stock:
            try:
                if not cookie in already_added:
                    already_added.append(cookie)
                    values = (str(cookie))
                    cursor.execute(f"INSERT INTO {name}(cookie) VALUES(?)",(values,))
                else:
                    dupe_amount += 1
            except Exception as e:
                print(e)
                pass
        con.commit()
        cursor.close()
        return dupe_amount
    else:
        for account in stock:
            try:
                if not account in already_added:
                    already_added.append(account)
                    accs = str(account).split(":")
                    values = (accs[0], accs[1])
                    cursor.execute(f"INSERT INTO {name}(username,password) VALUES(?,?)",values)
                else:
                    dupe_amount += 1
            except:
                pass
        con.commit()
        cursor.close()
        return dupe_amount

async def getStock():
    stock = []
    cursor = con.cursor()
    for service in service_list:
        name = f'accounts_{service}'
        cursor.execute(f"SELECT COUNT(*) FROM {name}")
        row_count = cursor.fetchone()[0]
        txt_cnt = "Out of stock" if row_count <= 0 else row_count
        stock.append(f"{service}:{txt_cnt}")
    for service in cookie_service_list:
        name = f'cookie_{service}'
        cursor.execute(f"SELECT COUNT(*) FROM {name}")
        row_count = cursor.fetchone()[0]
        txt_cnt = "Out of stock" if row_count <= 0 else row_count
        stock.append(f"{service}:{txt_cnt}")
    cursor.close()
    return stock

async def getPremiumStock():
    stock = []
    cursor = con.cursor()
    for service in premium_service_list:
        name = f'paccounts_{service}'
        cursor.execute(f"SELECT COUNT(*) FROM {name}")
        row_count = cursor.fetchone()[0]
        txt_cnt = "Out of stock" if row_count <= 0 else row_count
        stock.append(f"{service}:{txt_cnt}")
    for service in premium_cookie_service_list:
        name = f'pcookie_{service}'
        cursor.execute(f"SELECT COUNT(*) FROM {name}")
        row_count = cursor.fetchone()[0]
        txt_cnt = "Out of stock" if row_count <= 0 else row_count
        stock.append(f"{service}:{txt_cnt}")
    cursor.close()
    return stock
    

async def getAccount(service):
    cursor = con.cursor()
    name, iscookie, ispremium = await getName(service)
    cursor.execute(f"SELECT COUNT(*) FROM {name}")
    row_count = cursor.fetchone()[0]
    if row_count > 0:
        cursor.execute(f"SELECT * FROM {name} ORDER BY RANDOM() LIMIT 1")
        account = cursor.fetchone()
        if iscookie:
            cursor.execute(f"DELETE FROM {name} WHERE cookie = '{account[0]}'")
        else:
            cursor.execute(f"DELETE FROM {name} WHERE username = '{account[0]}' AND password = '{account[1]}'")
        con.commit()
        cursor.close()
        return True,account,iscookie
    else:
        cursor.close()
        return False,None,False

async def service_autcom(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    types = Abkradam
    return [
        app_commands.Choice(name=service, value=service)
        for service in types if current.lower() in service.lower()
    ]

def cooldown(interaction: discord.Interaction):
    isPremium = interaction.user.get_role(int(config['roles']["premium-role"]))
    isBooster = interaction.user.get_role(int(config['roles']["booster-role"]))
    if interaction.user.id in config['admins']:
        return None
    elif isPremium:
        return app_commands.Cooldown(1, str(timedelta(minutes=config['cooldowns']['premium']).total_seconds()))
    elif isBooster:
        return app_commands.Cooldown(1, str(timedelta(minutes=config['cooldowns']['booster']).total_seconds()))
    else:
        return app_commands.Cooldown(1, str(timedelta(minutes=config['cooldowns']['normal']).total_seconds()))

@tree.command(name = "generate", description = "Generate an account of your choice.", guild=discord.Object(id=config["guild-id"]))
@app_commands.autocomplete(service=service_autcom)
@app_commands.checks.dynamic_cooldown(cooldown)
async def generate(interaction: discord.Interaction, service: str):
    try:
        
        if not interaction.user.id in config['admins'] and not interaction.user.get_role(int(config['roles']["free-role"])):
            return await interaction.response.send_message(str(config['messages']['noperms']), ephemeral=True)
        
        if not interaction.user.id in config['admins'] and not interaction.channel_id in config["gen-channels"]:
            channel_list = [f"<#{channel}>" for channel in config["gen-channels"]]
            return await interaction.response.send_message(str(config['messages']['wrongchannel']) + ', '.join(channel_list), ephemeral=True)
        
        if not service in Abkradam:
            types = [typez for typez in Abkradam]
            return await interaction.response.send_message(f'Invalid service. Service list: `{types}`', ephemeral=True)
        
        if not interaction.user.id in config['admins'] and not interaction.user.get_role(int(config['roles']["premium-role"])):
            name, iscookie, ispremium = await getName(service)
            if ispremium:
                return await interaction.response.send_message(f'You need to have the premium role to use this command.', ephemeral=True) 
        
        # get one of the accounts from stock
        success, account, iscookie = await getAccount(service)
        
        # respond
        if not success:
            app_commands.Cooldown(1, str(timedelta(minutes=config['cooldowns']['error']).total_seconds()))
            return await interaction.response.send_message(f"There is no stock left.", ephemeral=True)
        
        if iscookie:
            channel = await interaction.user.create_dm()
            embd=discord.Embed(title="Account Generated :label: ",description=config['messages']['altsent'],color=config['colors']['success']) 
            if config['messages']['cookie-altmessage-switch']:
                await channel.send(embed=embd)
            embd2=discord.Embed(title=f"`{service}` generated :label: ",description=':incoming_envelope: Check your DMs for the cookie.',color=config['colors']['success'])
            embd2.set_footer(text='github.com/Atluzka/account-gen-bot',icon_url=interaction.user.avatar.url)
            embd2.set_image(url=config["generate-settings"]["gif-img-url"])
            await channel.send(file=discord.File(fp=StringIO(account['cookie']), filename=f'{service}.txt'))
            return await interaction.response.send_message(embed=embd2, ephemeral=False)
        
        else:
            channel = await interaction.user.create_dm()
            embd=discord.Embed(title="Account Generated :label: ",description=config['messages']['altsent'] + f"\n```{account['username']}:{account['password']}```",color=config['colors']['success']) 
            embd.set_footer(text='github.com/Atluzka/account-gen-bot',icon_url=interaction.user.avatar.url)
            embd2=discord.Embed(title=f"`{service}` generated :label: ",description=':incoming_envelope: Check your DMs for the account.',color=config['colors']['success'])
            embd2.set_footer(text='github.com/Atluzka/account-gen-bot',icon_url=interaction.user.avatar.url)
            embd2.set_image(url=config["generate-settings"]["gif-img-url"])
            await channel.send(embed=embd)
            return await interaction.response.send_message(embed=embd2, ephemeral=False)
    except Exception as e:
        return await interaction.response.send_message(f'```rust\n{e}```', ephemeral=True)


@generate.error
async def gencmd_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        embd=discord.Embed(title="Cooldown",description=f':no_entry_sign: This command is on cooldown, try again in {(error.retry_after/60):.2f} minutes.',color=config['colors']['error'])
        await interaction.response.send_message(embed=embd, ephemeral=False)

@tree.command(name = "addstock", description = "Add stock to database (admin only)", guild=discord.Object(id=config["guild-id"]))
async def addaccounts(interaction: discord.Interaction, service: str, file: discord.Attachment):
    
    # check if user is admin
    if not interaction.user.id in config['admins']:
        return await interaction.response.send_message(str(config['messages']['noperms']), ephemeral=True)
    
    if not str(service) in Abkradam:
        return await interaction.response.send_message(f'Invalid service', ephemeral=True)
    # check the file extension
    try:
        if not str(file.filename).split('.')[1] == 'txt':
            return await interaction.response.send_message(f'You can only upload files with .txt extension', ephemeral=True)
    except:
        return await interaction.response.send_message(f'You can only upload files with .txt extension', ephemeral=True)
    # check the size of the file
    if file.size > config["maximum-file-size"]:
        return await interaction.response.send_message(f'Maximum file size: `{config["maximum-file-size"]} bytes`', ephemeral=True)
    content = await file.read()
    
    name, iscookie, ispremium = await getName(service)
    
    filtered_stock = []
    if iscookie:
        current_cookie = ""
        dec_cont = content.decode('utf-8')
        content = str(dec_cont).split("\r\n")
        append_lines = False
        for line in content:
            if config['cookie-seperator'] in line:
                if len(current_cookie) > 0:
                    filtered_stock.append(current_cookie)
                    current_cookie = ""
                append_lines = not append_lines
            elif append_lines:
                current_cookie += line + '\n'
    else:
        dec_cont = content.decode('utf-8')
        content = str(dec_cont).split("\r\n")
        for item in content:
            if len(item) > 2:
                filtered_stock.append(item)
    dupe_amount = await addStock(name, filtered_stock, iscookie)
    
    if iscookie:
        return await interaction.response.send_message(f'`{len(filtered_stock)}` cookies have been added to the `{service}` database. `{dupe_amount}` dupes found.', ephemeral=True)
    return await interaction.response.send_message(f'`{len(filtered_stock)}` accounts have been added to the `{service}` database. `{dupe_amount}` dupes found.', ephemeral=True)

async def createservice_autcom(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    types = ["cookie", "premium", "free", "premium cookie"]
    return [
        app_commands.Choice(name=type, value=type)
        for type in types if current.lower() in type.lower()
    ]

@tree.command(name = "createservice", description = "Create a service (admin only)", guild=discord.Object(id=config["guild-id"]))
@app_commands.autocomplete(type=createservice_autcom)
async def stock(interaction: discord.Interaction, servicename: str, type: str):
    if not interaction.user.id in config['admins']:
        return await interaction.response.send_message(str(config['messages']['noperms']), ephemeral=True)
    cursor = con.cursor()
    if type == 'premium':
        cursor.execute(f'CREATE TABLE IF NOT EXISTS paccounts_{servicename}(username TEXT NOT NULL, password TEXT NOT NULL)')
        con.commit()
        await getServices()
        return await interaction.response.send_message(f'`{servicename}` premium service has been made', ephemeral=True)
    elif type == 'free':
        cursor.execute(f'CREATE TABLE IF NOT EXISTS accounts_{servicename}(username TEXT NOT NULL, password TEXT NOT NULL)')
        con.commit()
        await getServices()
        return await interaction.response.send_message(f'`{servicename}` service has been made', ephemeral=True)
    elif type == 'cookie':
        cursor.execute(f'CREATE TABLE IF NOT EXISTS cookie_{servicename}(cookie TEXT NOT NULL)')
        con.commit()
        await getServices()
        return await interaction.response.send_message(f'`{servicename}` cookie service has been made', ephemeral=True)
    elif type == 'premium cookie':
        cursor.execute(f'CREATE TABLE IF NOT EXISTS pcookie_{servicename}(cookie TEXT NOT NULL)')
        con.commit()
        await getServices()
        return await interaction.response.send_message(f'`{servicename}` premium cookie service has been made', ephemeral=True)
    else:
        return await interaction.response.send_message(f'Invalid service type.', ephemeral=True)

    
@tree.command(name = "deleteservice", description = "Delete a service (admin only)", guild=discord.Object(id=config["guild-id"]))
@app_commands.autocomplete(service=service_autcom)
async def stock(interaction: discord.Interaction, service: str):
    # check if user is admin
    if not interaction.user.id in config['admins']:
        return await interaction.response.send_message(str(config['messages']['noperms']), ephemeral=True)
    cursor = con.cursor()
    yes = Button(label='Yes', style=discord.ButtonStyle.green)
    cancel = Button(label='Cancel', style=discord.ButtonStyle.red)
    async def true_button_callback(interaction):
        name, iscookie, ispremium = await getName(service)
        try:
            cursor.execute(f"DROP TABLE {name}")
        except Exception as e:
            return await interaction.response.edit_message(content=f'```{e}```', view=None)
        con.commit()
        await getServices()
        return await interaction.response.edit_message(content=f'`{service}` has been deleted', view=None)
    async def false_button_callback(interaction):
        return await interaction.response.edit_message(content=f'Interaction canceled', view=None)
    yes.callback = true_button_callback
    cancel.callback = false_button_callback
    view = View()
    view.add_item(yes)
    view.add_item(cancel)
    await interaction.response.send_message('Are you sure? Deleting a service will also delete the stock with it.', view=view, ephemeral=True)
    

@tree.command(name = "stock", description = "Get the amount of stock", guild=discord.Object(id=config["guild-id"]))
async def stock(interaction: discord.Interaction):
    stock = await getStock()
    prem_stock = await getPremiumStock()
    if len(stock) <= 0 and len(prem_stock) <= 0:
        embd=discord.Embed(title=f"Stock - 0 services",description='There are no services to display',color=config['colors']['stock'])
        embd.set_footer(text='github.com/Atluzka/account-gen-bot')
        return await interaction.response.send_message(embed=embd)
    filtered_stock = [] 
    for stk in prem_stock:
        stk = (stk.split(':'))
        filtered_stock.append(f":star: **{stk[0]}**: `{stk[1]}`")
    for stk in stock:
        stk = (stk.split(':'))
        filtered_stock.append(f"**{stk[0]}**: `{stk[1]}`")
    #random.shuffle(filtered_stock)
    embd=discord.Embed(title=f"Stock - {len(filtered_stock)} services",description='\n'.join(filtered_stock),color=config['colors']['stock'])
    embd.set_footer(text='github.com/Atluzka/account-gen-bot')
    return await interaction.response.send_message(embed=embd)
bot.run(config['token'])
