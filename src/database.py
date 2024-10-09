async def getServices(con):
    serviceslist = []
    cur = con.cursor(); cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = cur.fetchall(); cur.close()
    for table in table_names:
        if str(table[0]).split('_')[0] == 'accounts':
            serviceslist.append(str(table[0]).split('_')[1].lower())
    return serviceslist

async def createService(con, table_name, servicelist):
    if table_name.lower() not in servicelist:
        cur = con.cursor()
        cur.execute(f'CREATE TABLE IF NOT EXISTS accounts_{table_name.lower()}(combo TEXT NOT NULL)')
        con.commit()
        cur.close()
        return True
    else:
        return False

async def deleteService(con, table_name, servicelist):
    if table_name.lower() in servicelist:
        cur = con.cursor()
        cur.execute(f"DROP TABLE accounts_{table_name.lower()}")
        con.commit()
        cur.close()
        return True
    else:
        return False
    
async def getAccount(con, service):
    cursor = con.cursor()
    name = f"accounts_{service}"
    cursor.execute(f"SELECT COUNT(*) FROM {name}")
    row_count = cursor.fetchone()[0]
    if row_count > 0:
        cursor.execute(f"SELECT * FROM {name} ORDER BY RANDOM() LIMIT 1")
        account = cursor.fetchone()
        cursor.execute(f"DELETE FROM {name} WHERE combo = '{account[0]}'")
        con.commit()
        cursor.close()
        return True,account
    else:
        cursor.close()
        return False,None
    
async def getMultipleAccounts(con, service, count):
    cursor = con.cursor()
    name = f"accounts_{service}"
    cursor.execute(f"SELECT COUNT(*) FROM {name}")
    row_count = cursor.fetchone()[0]

    if row_count >= count:
        cursor.execute(f"SELECT * FROM {name} ORDER BY RANDOM() LIMIT {count}")
        accounts = cursor.fetchall()
        accounts_list = [account['combo'].strip() for account in accounts]
        for account in accounts:
            cursor.execute(f"DELETE FROM {name} WHERE combo = '{account[0]}'")
        con.commit()
        cursor.close()
        return True, accounts_list, row_count
    else:
        cursor.close()
        return False, None, row_count

async def addStock(con, service, stock, remove_capture):
    cursor = con.cursor()
    dupe_amount = 0
    already_added = []
    for account in stock:
        try:
            if not account in already_added:
                already_added.append(account)
                if "|" in account and remove_capture:
                    account = account.split('|')[0]
                values = (account)
                cursor.execute(f"INSERT INTO accounts_{service}(combo) VALUES(?)",(values,))
            else:
                dupe_amount += 1
        except Exception as e:
            print(e)
    con.commit()
    cursor.close()
    return len(already_added),dupe_amount

async def getStock(con, serviceList):
    stock = []
    cursor = con.cursor()
    for service in serviceList:
        name = f'accounts_{service}'
        cursor.execute(f"SELECT COUNT(*) FROM {name}")
        row_count = cursor.fetchone()[0]
        txt_cnt = "Out of stock" if row_count <= 0 else row_count
        stock.append(f"{service}:{txt_cnt}")
    return stock