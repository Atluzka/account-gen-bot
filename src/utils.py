async def does_user_meet_requirements(user_roles, config, service_input):
    try:
        user_roles = [role.id for role in user_roles]
        for role in config["roles"]:
            if role['id'] in user_roles:
                if service_input in role['gen-access'] or "all" in role['gen-access']:
                    return True
        return False
    except:
        pass