import discord, os, glob, json, datetime
from discord import app_commands

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

directory = os.getcwd()
configfile = open(directory + '/config.json')
config = json.load(configfile)

#didnt work when i added this to the config file. might work with json5
embed_color = 0x2b2d31

if not os.path.exists(directory + '/accounts'): 
    os.mkdir(directory + '/accounts')
if not os.path.exists(directory + '/paccounts'): 
    os.mkdir(directory + '/paccounts')

async def sendLog(interaction, account, premium):
    channel = bot.get_channel(int(config["logs-channel-id"]))
    author_name = interaction.user.name + "#" + interaction.user.discriminator
    embed=discord.Embed()
    embed.set_author(name=author_name + ' - ' + str(interaction.user.id),icon_url=interaction.user.avatar.url)
    embed.description=f"```{account}```"
    embed.set_footer(text="Generator Log")
    embed.timestamp = datetime.datetime.now()
    if premium:
        embed.color=0xebb733
    else:
        embed.color=0x2B2D31
    await channel.send(embed=embed)
    return

async def simpleEmbed(interaction, message, ephemeral):
    embed=discord.Embed()
    embed.description=f"{message}"
    embed.color=0x2B2D31
    await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

async def getFileName(file):
    file_name = file.split('\\', -1)[-1]
    return file_name.split('.', -1)[0]

async def getAccs(p):
    allAccounts = []
    if not p:
        for file in glob.glob(directory + '/accounts/*.txt'):
            with open(file, 'r', encoding='utf-8') as fp:
                x = len(fp.readlines())
            allAccounts.append(await getFileName(file) + ":" + str(x))
    else:
        for file in glob.glob(directory + '/paccounts/*.txt'):
            with open(file, 'r', encoding='utf-8') as fp:
                x = len(fp.readlines())
            allAccounts.append(await getFileName(file) + ":" + str(x))
    return allAccounts

async def accountDisplay(account_list):
    new_acc_list = []
    for i in account_list:
        rndmlist1 = i.split(":", 1)
        rndmlist1[1] = "`" + rndmlist1[1] + "`"
        new_acc_list.append(rndmlist1[0].upper() + " -> " + rndmlist1[1])
    return new_acc_list

@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=config["guild-id"]))
    print("Bot: {0.user}".format(bot))

@bot.event
async def on_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CommandNotFound):
        print("Helo")
        await simpleEmbed(interaction, "Command not found", True)

def normal_cooldown(interaction: discord.Interaction): 
    if not config['admin-cooldown'] and interaction.user.guild_permissions.administrator:
        return None
    else:
        return app_commands.Cooldown(1, config['cooldown-duration'])

@tree.command(name = "gen", description = "Generate an account.", guild=discord.Object(id=config["guild-id"]))
@app_commands.checks.dynamic_cooldown(normal_cooldown)
async def gen(interaction: discord.Interaction, account: str):
    if not str(interaction.channel_id) in config["free-gen-channels"] and config["channel-specific-switch"]:
        await simpleEmbed(interaction, config["messages"]["not-supported-channel"], True)
        return
    channel = await interaction.user.create_dm()
    for file in glob.glob(directory + '/accounts/*.txt'):
        file_name = file.split('\\', -1)[-1]
        file_name = file_name.split('.', -1)[0]
        if file_name.lower() == account.lower():
            if os.stat(file).st_size == 0:
                await interaction.response.send_message("`" + file_name.upper() + "` is out of stock.")
                return
            with open(file, "r+", encoding = "utf-8") as fp:
                fp.seek(0, os.SEEK_END)
                pos = fp.tell() - 1
                while pos > 0 and fp.read(1) != "\n":
                    pos -= 1
                    fp.seek(pos, os.SEEK_SET)
                acc_line = fp.readline()
                if pos > 0:
                    fp.seek(pos, os.SEEK_SET)
                    fp.truncate()
            genembed=discord.Embed(title="Generated Account - " + file_name,
                        description="```" + acc_line +"```",
                        color=embed_color)
            genembed.set_footer(text=config["messages"]["embed-footer"])
            await channel.send(embed=genembed)
            await simpleEmbed(interaction, config["messages"]["account-generated"], False)
            if config["logs-switch"]:
                await sendLog(interaction, acc_line, False)
            return
    await simpleEmbed(interaction, config["messages"]["service-doesnt-exist"], True)

@gen.error
async def gencmd_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f'This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.', ephemeral=True)

def premium_cooldown(interaction: discord.Interaction):
    if not config['admin-cooldown'] and interaction.user.guild_permissions.administrator:
        return None
    elif not config['premium-cooldown']:
        return None
    else:
        return app_commands.Cooldown(1, config['premium-cooldown-duration'])

@tree.command(name = "pgen", description = "Generate an premium account.", guild=discord.Object(id=config["guild-id"]))
@app_commands.checks.has_role(int(config['premium-role-id']))
@app_commands.checks.dynamic_cooldown(premium_cooldown)
async def pgen(interaction: discord.Interaction, account: str):
    if not str(interaction.channel_id) in config["premium-gen-channels"] and config["channel-specific-switch"]:
        await simpleEmbed(interaction, config["messages"]["not-supported-channel"], True)
        return
    channel = await interaction.user.create_dm()
    for file in glob.glob(directory + '/paccounts/*.txt'):
        file_name = file.split('\\', -1)[-1]
        file_name = file_name.split('.', -1)[0]
        if file_name.lower() == account.lower():
            if os.stat(file).st_size == 0:
                await interaction.response.send_message("`" + file_name.upper() + "` is out of stock.")
                return
            with open(file, "r+", encoding = "utf-8") as fp:
                fp.seek(0, os.SEEK_END)
                pos = fp.tell() - 1
                while pos > 0 and fp.read(1) != "\n":
                    pos -= 1
                    fp.seek(pos, os.SEEK_SET)
                acc_line = fp.readline()
                if pos > 0:
                    fp.seek(pos, os.SEEK_SET)
                    fp.truncate()
            genembed=discord.Embed(title="Premium Generated Account - " + file_name,
                        description="```" + acc_line +"```",
                        color=embed_color)
            genembed.set_footer(text=config["messages"]["embed-footer"])
            await channel.send(embed=genembed)
            await simpleEmbed(interaction, config["messages"]["account-generated"], False)
            if config["logs-switch"]:
                await sendLog(interaction, acc_line, True)
            return
    await simpleEmbed(interaction, config["messages"]["service-doesnt-exist"], True)

@pgen.error
async def gencmd_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingRole):
        await interaction.response.send_message(config["messages"]["no-permissions"], ephemeral=True)
    elif isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f'This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.', ephemeral=True)

@tree.command(name = "create", description = "Creates a new service. (ADMIN ONLY)", guild=discord.Object(id=config["guild-id"]))
@app_commands.checks.has_permissions(administrator=True)
async def create(interaction: discord.Interaction, premium: bool, name: str):
    if premium:
        if not os.path.exists(directory + '/paccounts'): 
            os.mkdir(directory + '/paccounts')
        open(directory + "/paccounts/" + name.lower() + ".txt", "x")
        await interaction.response.send_message("Created new service: ``" + name.lower() + "``")

    elif not premium:
        if not os.path.exists(directory + '/accounts'): 
            os.mkdir(directory + '/accounts')
        open(directory + "/accounts/" + name.lower() + ".txt", "x")
        await interaction.response.send_message("Created new service: ``" + name.lower() + "``")
    else:
        await interaction.response.send_message("Error?", ephemeral=True)

@tree.command(name = "add", description = "Adds an account to a service. (ADMIN ONLY)", guild=discord.Object(id=config["guild-id"]))
@app_commands.checks.has_permissions(administrator=True)
async def addacc(interaction: discord.Interaction, premium: bool, service: str, account: str):
    if premium:
        for file in glob.glob(directory + '/paccounts/*.txt'):
            if getFileName(file).lower() == service.lower():
                with open(file) as fp:
                    text = fp.read()
                    fp.close()
                with open(file, 'a') as fp:
                    if not text.endswith('\n') and fp.tell() != 0:
                        fp.write('\n')
                    fp.write(account)
                    fp.close()
                await interaction.response.send_message("Operation successful", ephemeral=True)
    elif not premium:
        for file in glob.glob(directory + '/paccounts/*.txt'):
                if getFileName(file).lower() == service.lower():
                    with open(file) as fp:
                        text = fp.read()
                    with open(file, 'a') as fp:
                        if not text.endswith('\n') and fp.tell() != 0:
                            fp.write('\n')
                        fp.write(account)
                    await interaction.response.send_message("Operation successful", ephemeral=True)
    else:
        await interaction.response.send_message("Error?", ephemeral=True)

@tree.command(name = "stock", description = "Get the amount of stock.", guild=discord.Object(id=config["guild-id"]))
async def stock(interaction: discord.Interaction):
    
    service_num = 0
    embed=discord.Embed(title="Stock",
                        description=config["messages"]["stock-description"],
                        color=embed_color)
    
    p = False
    account_list = await getAccs(p)
    new_acc_list = []

    if not len(account_list) <= 0:
        new_acc_list = await accountDisplay(account_list)
        embed.add_field(name="Free Generator", value='\n'.join(new_acc_list), inline=False)
        service_num = len(new_acc_list)
        del new_acc_list, account_list

    new_acc_list = []
    account_list = await getAccs(p = True)
    if not len(account_list) <= 0:
        new_acc_list = await accountDisplay(account_list)
        service_num = len(new_acc_list) + service_num
        embed.add_field(name="Premium Generator", value='\n'.join(new_acc_list), inline=False)

    if service_num <= 0:
        embed.description = config["messages"]["stock-empty-description"]

    embed.title = "Stock - " + str(service_num) +  " Services"
    
    embed.set_footer(text=config["messages"]["embed-footer"])
    await interaction.response.send_message(embed=embed)

bot.run(config['token'])
