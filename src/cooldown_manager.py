import discord, json
from datetime import datetime, timedelta

config = json.load(open('config.json'))

template_data = {
    'success': False,
    'formatedCooldownMsg': '',
    'stillHasCooldown': False,
    'secondsTillEnd': 0,
    'endTime': 0
}

def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours} hours, {minutes} minutes and {seconds} seconds."
    elif minutes > 0:
        return f"{minutes} minutes and {seconds} seconds."
    else:
        return f"{seconds} seconds."

async def getCooldownData(list_of_users_with_cooldown, userid):
    user = None
    cooldown_end_time = None
    for _user in list_of_users_with_cooldown:
        id, cooldown = _user.split(":")
        if str(id) == str(userid):
            user = _user
            cooldown_end_time = cooldown
            break
    _data = template_data
    if not user:
        return _data
    current_time = datetime.now().timestamp()
    _data['success'] = True
    _data['secondsTillEnd'] = 0 if int(int(cooldown_end_time) - current_time) <= 0 else int(int(cooldown_end_time) - current_time)
    _data['formatedCooldownMsg'] = "This command is on cooldown, try again in %s" % (format_time(_data['secondsTillEnd']))
    _data['stillHasCooldown'] = True if _data['secondsTillEnd'] > 0 else False
    _data['endTime'] = int(cooldown_end_time)
    return _data

async def get_role_user_cooldown(interaction: discord.Interaction):
    if not config["commands-give-cooldown"]:
        return None
    if interaction.user.id in config['admins']:
        return None
    userRoles = [role.id for role in interaction.user.roles]
    minCooldown = float("inf")

    # Get the minimum cooldown the user can have.
    for role in config["roles"]:
        if int(role["id"]) in userRoles and float(role["cooldown"]) < minCooldown:
            minCooldown = float(role["cooldown"])

    current_time = datetime.now().timestamp()
    if not minCooldown == float("inf"):
        return current_time + int(minCooldown)
    else:
        return current_time + int(config['roles'][0]["cooldown"])

async def does_user_have_cooldown(user_cooldowns, userid):
    user = None
    for _user in user_cooldowns:
        id, _c = _user.split(":")
        if str(id) == str(userid):
            user = _user
            break
    if not user:
        return False
    else:
        return True

    