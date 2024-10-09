async def does_user_meet_requirements(user_roles, config, service_input, isbulkgen=False):
    try:
        if isbulkgen:
            user_roles = [role.id for role in user_roles]
            canbulkgen = False
            for role in config["roles"]:
                if role['id'] in user_roles:
                    if service_input in role['gen-access'] or "all" in role['gen-access']:
                        canbulkgen = True if role['can-bulk-gen'] == True else False
                        max_gen_amnt = role['bulk-gen-max']
                        return True, canbulkgen, max_gen_amnt
            return False
        else:
            user_roles = [role.id for role in user_roles]
            for role in config["roles"]:
                if role['id'] in user_roles:
                    if service_input in role['gen-access'] or "all" in role['gen-access']:
                        return True
            return False
    except:
        #print('There was an error while trying to check for requirements')
        pass