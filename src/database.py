from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Integer, Boolean, Text, func, JSON, delete
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.mutable import MutableDict

import json, discord

config = json.load(open('config.json'))

Base = declarative_base()
engine = create_async_engine("sqlite+aiosqlite:///database.db")
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    service_name = Column(String, index=True)
    combo = Column(String, nullable=False)

class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True)
    last_time_genned = Column(String, nullable=True)
    amount_genned = Column(Integer, default=0)
    prem_amount_genned = Column(Integer, default=0)
    is_blacklisted = Column(Boolean, default=False)
    custom_cooldown = Column(MutableDict.as_mutable(JSON), default={"Free": None, "Premium": None})
    user_cooldown = Column(MutableDict.as_mutable(JSON), default={"Free": None, "Premium": None})
    subscription_time_left = Column(Integer, nullable=True)
    subscription_stage = Column(String, default="Free")
    notes = Column(Text, nullable=True)

    async def update_gen_count(self, amount: int = 1, is_premium: bool = False):
        if is_premium:
            self.prem_amount_genned += int(amount)
        else:
            self.amount_genned += int(amount)
        self.last_time_genned = str(datetime.now(timezone.utc).timestamp())

        async with Session() as session:
            session.add(self)
            await session.commit()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def getServices():
    async with Session() as session:
        services = (await session.execute(select(Account.service_name).distinct()))
        return services.scalars().all()

async def deleteService(service_name):
    async with Session() as session:
        stmt = delete(Account).where(Account.service_name == service_name.lower())
        await session.execute(stmt)
        await session.commit()
        return True

async def getAccount(service_name):
    combo = ""
    async with Session() as session:
        account = (await session.execute(select(Account).filter_by(service_name=service_name.lower()).order_by(func.random()))).scalars().first()
        if account:
            combo = account.combo
            await session.delete(account)
            await session.commit()
        else:
            return False, None
    return True, str(combo).strip()

async def getMultipleAccounts(service_name: str, amount: int):
    combos = []
    async with Session() as session:
        query = (
            select(Account)
            .filter_by(service_name=service_name.lower())
            .order_by(func.random())
            .limit(int(amount))
        )
        result = await session.execute(query)
        accounts = result.scalars().all()

        if accounts:
            for account in accounts:
                combo = account.combo
                combos.append(str(combo).strip())
                await session.delete(account)
            await session.commit()
        else:
            return False, None

    return True, combos

async def addStock(service_name, stock, remove_capture):
    async with Session() as session:
        existing_combos = (
            await session.execute(
                select(Account.combo).filter_by(service_name=service_name.lower())
            )
        ).scalars().all()
        existing_combos_set = set(existing_combos)
        
        added_accounts = []
        duplicate_count = 0
        
        for account in stock:
            try:
                combo = account.split("|")[0] if remove_capture and "|" in account else account
            except Exception:
                combo = account
            if combo in existing_combos_set:
                duplicate_count += 1
            else:
                added_accounts.append(Account(service_name=service_name.lower(), combo=combo))
                existing_combos_set.add(combo)

        if added_accounts:
            session.add_all(added_accounts)
            await session.commit()

        return len(added_accounts), duplicate_count


async def getStock(service_list):
    async with Session() as session:
        stock = []
        for service in service_list:
            count = (await session.execute(select(func.count(Account.id)).filter_by(service_name=service.lower()))).scalar()
            stock.append(f"{service}: {'0' if count == 0 else count}")
        return stock

async def addUser(user_id):
    async with Session() as session:
        user = (await session.execute(select(User).filter_by(user_id=user_id))).scalars().first()
        if not user:
            user = User(
                user_id=user_id,
                subscription_stage="Free"
            )
            session.add(user)
            await session.commit()
        user = (await session.execute(select(User).filter_by(user_id=user_id))).scalars().first()
        if not user: # wtf
            return None
        return user

async def getUser(user_id):
    async with Session() as session:
        user = (await session.execute(select(User).filter_by(user_id=user_id))).scalars().first()
        if not user:
            return None
        return user

async def set_subscription(user_id: str, subscription_time: int, reset_sub: bool=False):
    async with Session() as session:
        user = (await session.execute(select(User).filter_by(user_id=user_id))).scalars().first()

        if not user:
            return False
        
        if reset_sub:
            user.subscription_time_left = None
            user.subscription_stage = "Free"
        else:
            current_time = datetime.now(timezone.utc).timestamp()
            user.subscription_time_left = current_time + subscription_time
            user.subscription_stage = "Premium"
        
        await session.commit()
        return True

async def has_subscription_left(user_id: str) -> bool:
    async with Session() as session:
        user = (await session.execute(select(User).filter_by(user_id=user_id))).scalars().first()

        if not user or not user.subscription_time_left:
            return False
        current_time = datetime.now(timezone.utc).timestamp()
        if float(current_time) <= float(user.subscription_time_left):
            return True
        else:
            await set_subscription(user_id, 0, True)
            return False

async def view_subscription(user_id: str):
    async with Session() as session:
        user = (await session.execute(select(User).filter_by(user_id=user_id))).scalars().first()

        if not user:
            return {
                'user': None
            }
        return {
            'user': user.user_id,
            'subscription_time_left': user.subscription_time_left,
            'subscription_stage': user.subscription_stage
        }
    
async def add_subscription(user_id: str, subscription_time: int):
    async with Session() as session:
        user = (await session.execute(select(User).filter_by(user_id=user_id))).scalars().first()

        if not user:
            return False

        if str(user.subscription_stage) != "Free":
            resp = await has_subscription_left(user_id)
            if resp:
                user.subscription_time_left = user.subscription_time_left + subscription_time
                await session.commit()
            else:
                await set_subscription(user_id, subscription_time)
        else:
            await set_subscription(user_id, subscription_time)
    return True

async def mass_add_subscription(subscription_time: int):
    async with Session() as session:
        premium_users = (await session.execute(select(User).filter_by(subscription_stage="Premium"))).scalars().all()

        if not premium_users:
            return None

        for user in premium_users:
            resp = await has_subscription_left(user.user_id)
            if resp:
                user.subscription_time_left += subscription_time
            else:
                await set_subscription(user.user_id, subscription_time)

        await session.commit()
    return len(premium_users)


template_data = {
    'success': False,
    'formatedCooldownMsg': '',
    'stillHasCooldown': False,
    'secondsTillEnd': 0,
    'endTime': 0
}    

def format_time(seconds):
    seconds = round(seconds, 2)
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"**{str(int(hours))} hours, {str(int(minutes))} minutes and {round(seconds, 2)} seconds.**"
    elif minutes > 0:
        return f"**{str(int(minutes))} minutes and {round(seconds, 2)} seconds.**"
    else:
        return f"**{round(seconds, 2)} seconds.**"

async def getCooldownData(user_id: str, stage: str):
    async with Session() as session:
        user = (await session.execute(select(User).filter_by(user_id=user_id))).scalars().first()
        _data = template_data

        if not user or not user.user_cooldown or not user.user_cooldown.get(stage):
            return _data

        current_time = datetime.now(timezone.utc).timestamp()
        cooldown_end_time = float(user.user_cooldown[stage])
        seconds_remaining = max(0, cooldown_end_time - current_time)
    
        _data['success'] = True
        _data['secondsTillEnd'] = seconds_remaining
        _data['formatedCooldownMsg'] = "This command is on cooldown, try again in %s" % format_time(seconds_remaining)
        _data['stillHasCooldown'] = seconds_remaining > 0
        _data['endTime'] = cooldown_end_time
        return _data

async def does_user_have_cooldown(user_id: str, stage: str):
    async with Session() as session:
        user = (await session.execute(select(User).filter_by(user_id=user_id))).scalars().first()
        if not user or not user.user_cooldown or not user.user_cooldown.get(stage):
            return False

        current_time = datetime.now().timestamp()
        return int(user.user_cooldown[stage]) > current_time


async def get_role_user_cooldown(interaction: discord.Interaction, roles, is_premium: bool=False):
    async with Session() as session:
        if not config["commands-give-cooldown"]:
            return None
        if any(role_id in config['admin-roles'] for role_id in roles):
            return None
        
        user = (await session.execute(select(User).filter_by(user_id=str(interaction.user.id)))).scalars().first()
        if not user:
            return None
        userRoles = [role.id for role in interaction.user.roles]
        minCooldown = float("inf")

        for role in config["roles"]:
            if is_premium:
                if int(role["id"]) in userRoles and float(role["premium-cooldown"]) < minCooldown:
                    minCooldown = float(role["premium-cooldown"])
            else:
                if int(role["id"]) in userRoles and float(role["free-cooldown"]) < minCooldown:
                    minCooldown = float(role["free-cooldown"])

        if user and user.custom_cooldown:
            stage_key = "Premium" if is_premium else "Free"
            custom_cooldown = user.custom_cooldown.get(stage_key)
            if custom_cooldown is not None:
                minCooldown = float(custom_cooldown)

        current_time = datetime.now().timestamp()
        cooldown_end = current_time + int(minCooldown if minCooldown != float("inf") else config['roles'][0]["default_cooldown"])

        user.user_cooldown[stage_key] = str(int(cooldown_end))
        await session.commit()
        
        return cooldown_end

async def set_user_cooldown(user_id: str, stage: str, cooldown_end_time: int):
    async with Session() as session:
        user = (await session.execute(select(User).filter_by(user_id=user_id))).scalars().first()
        if not user:
            await addUser(user_id)
            user = (await session.execute(select(User).filter_by(user_id=user_id))).scalars().first()
            
        if user.user_cooldown is None:
            user.user_cooldown = {"Free": None, "Premium": None}

        user.user_cooldown[stage] = int(cooldown_end_time)
        await session.commit()
        return True
    
async def set_user_custom_cooldown(user_id: str, stage: str, custom_cooldown: int):
    async with Session() as session:
        user = (await session.execute(select(User).filter_by(user_id=user_id))).scalars().first()
        if not user:
            await addUser(user_id)
            user = (await session.execute(select(User).filter_by(user_id=user_id))).scalars().first()

        if user.custom_cooldown is None:
            user.custom_cooldown = {"Free": None, "Premium": None}
        user.custom_cooldown[stage] = custom_cooldown
        await session.commit()
        return True

    
async def reset_user_custom_cooldown(user_id: str, stage: str):
    async with Session() as session:
        user = (await session.execute(select(User).filter_by(user_id=user_id))).scalars().first()
        if not user:
            await addUser(user_id)
            user = (await session.execute(select(User).filter_by(user_id=user_id))).scalars().first()
        user.custom_cooldown[stage] = None
        await session.commit()
        return True
    
async def reset_user_cooldown(user_id: str, stage: str):
    async with Session() as session:
        user = (await session.execute(select(User).filter_by(user_id=user_id))).scalars().first()
        if not user:
            await addUser(user_id)
            user = (await session.execute(select(User).filter_by(user_id=user_id))).scalars().first()
        
        current_time = datetime.now().timestamp()
        
        if user.user_cooldown is None:
            user.user_cooldown = {"Free": None, "Premium": None}

        user.user_cooldown[stage] = int(current_time)
        await session.commit()
        return True
    
async def blacklist_user(user_id: str, status: bool):
    async with Session() as session:
        user = (await session.execute(select(User).filter_by(user_id=user_id))).scalars().first()
        if not user:
            await addUser(user_id)
            user = (await session.execute(select(User).filter_by(user_id=user_id))).scalars().first()
        if status:
            user.is_blacklisted = status
            await session.commit()
            return status
        else:
            user.is_blacklisted = not user.is_blacklisted
            await session.commit()
            return user.is_blacklisted
        
async def set_user_note(user_id: str, note: str):
    async with Session() as session:
        user = (await session.execute(select(User).filter_by(user_id=user_id))).scalars().first()
        if not user:
            await addUser(user_id)
            user = (await session.execute(select(User).filter_by(user_id=user_id))).scalars().first()
        user.notes = note
        await session.commit()
        return True

