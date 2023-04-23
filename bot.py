import discord, os, glob, json
from discord.ext import commands

bot = commands.Bot(command_prefix=[".", "$"], intents=discord.Intents.all())
bot.remove_command('help')
directory = os.getcwd()

configfile = open(directory + '/config.json')
config = json.load(configfile)

#didnt work when i added this to the config file. might work with json5
embed_color = 0x2b2d31

if not os.path.exists(directory + '/accounts'): 
    os.mkdir(directory + '/accounts')
if not os.path.exists(directory + '/paccounts'): 
    os.mkdir(directory + '/paccounts')


def getFileName(file):
    file_name = file.split('\\', -1)[-1]
    return file_name.split('.', -1)[0]

def getAccs(p):
    allAccounts = []
    if not p:
        for file in glob.glob(directory + '/accounts/*.txt'):
            with open(file, 'r', encoding='utf-8') as fp:
                x = len(fp.readlines())
            allAccounts.append(getFileName(file) + ":" + str(x))
    else:
        for file in glob.glob(directory + '/paccounts/*.txt'):
            with open(file, 'r', encoding='utf-8') as fp:
                x = len(fp.readlines())
            allAccounts.append(getFileName(file) + ":" + str(x))
    return allAccounts

def accountDisplay(account_list):
    new_acc_list = []
    for i in account_list:
            rndmlist1 = i.split(":", 1)
            rndmlist1[1] = "`" + rndmlist1[1] + "`"
            new_acc_list.append(rndmlist1[0].upper() + " -> " + rndmlist1[1])
            return new_acc_list

@bot.event
async def on_ready():
    print("Bot: {0.user}".format(bot))
    
@bot.slash_command(name="gen", description="Generate an account.", guild_ids=[config['guild-id']])
async def gen(interaction: discord.Interaction, account: str):
    channel = await interaction.user.create_dm()
    for file in glob.glob(directory + '/accounts/*.txt'):
        file_name = file.split('\\', -1)[-1]
        file_name = file_name.split('.', -1)[0]
        if file_name.lower() == account.lower():
            if os.stat(file).st_size == 0:
                await interaction.response.send_message("`" + file_name.upper() + "` is out of stock.")
                return
            with open(file, "r+") as fp:
                lines = fp.readlines() 
                acc_line = lines[0]
                fp.seek(0)
                fp.truncate()
                fp.writelines(lines[1:])
            genembed=discord.Embed(title="Generated Account - " + file_name,
                        description="```" + acc_line +"```",
                        color=embed_color)
            genembed.set_footer(text="github.com/Atluzka/account-gen-bot")
            await channel.send(embed=genembed)
            await interaction.response.send_message("Generated account has been sent to your DMs")
            return
    await interaction.response.send_message("Service not found")

@bot.slash_command(name="pgen", description="Generate an premium account.", guild_ids=[config['guild-id']])
@commands.has_role(int(config['premium-role-id']))
async def gen(interaction: discord.Interaction, account: str):
    channel = await interaction.user.create_dm()
    for file in glob.glob(directory + '/paccounts/*.txt'):
        file_name = file.split('\\', -1)[-1]
        file_name = file_name.split('.', -1)[0]
        if file_name.lower() == account.lower():
            if os.stat(file).st_size == 0:
                await interaction.response.send_message("`" + file_name.upper() + "` is out of stock.")
                return
            with open(file, "r+") as fp:
                lines = fp.readlines() 
                acc_line = lines[0]
                fp.seek(0)
                fp.truncate()
                fp.writelines(lines[1:])
            genembed=discord.Embed(title="Premium Generated Account - " + file_name,
                        description="```" + acc_line +"```",
                        color=embed_color)
            genembed.set_footer(text="github.com/Atluzka/account-gen-bot")
            await channel.send(embed=genembed)
            await interaction.response.send_message("Generated account has been sent to your DMs")
            return
    await interaction.response.send_message("Service not found")

@gen.error
async def gencmd_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.MissingRole):
        await interaction.response.send_message("You don't have access to this command.")


@bot.slash_command(name="stock", description="Get the amount of stock.", guild_ids=[config['guild-id']])
async def stock(ctx):
    
    service_num = 0
    embed=discord.Embed(title="Stock", #service_num + 
                        description="All accounts available to be generated.", #'\n'.join(new_acc_list)
                        color=embed_color)
    
    p = False
    account_list = getAccs(p)
    new_acc_list = []

    if not len(account_list) <= 0:
        new_acc_list = accountDisplay(account_list)
        embed.add_field(name="Free Generator", value='\n'.join(new_acc_list), inline=False)
        service_num = len(new_acc_list)
        del new_acc_list, account_list

    new_acc_list = []
    account_list = getAccs(p = True)
    if not len(account_list) <= 0:
        new_acc_list = accountDisplay(account_list)
        service_num = len(new_acc_list) + service_num
        embed.add_field(name="Premium Generator", value='\n'.join(new_acc_list), inline=False)

    if service_num <= 0:
        embed.description = "There aren't any accounts to be generated."

    embed.title = "Stock - " + str(service_num) +  " Services"
    

    #embed.add_field("Free Accounts")
    embed.set_footer(text="github.com/Atluzka/account-gen-bot")
    await ctx.respond(embed=embed)

bot.run(config['token'])
