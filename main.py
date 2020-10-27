#!/usr/bin/env python3
from discord.ext import commands
import sys
import os
import asyncio
import secrets
import sqlite3
import pickle
import random
import threading
import time

bot = commands.Bot(command_prefix="se.")

#To save time, some policies are stored in memory
MAX_POLICY_CACHE = 15
cached_policies = {}

#Same done with user profiles
MAX_USER_CACHE = 50
cached_users = {}

#Used to determine when cache should be written
CACHE_UPDATED = False

#Setup sqlite3 db
if os.path.isdir("data"):
    db = sqlite3.connect("data/sediscord.db")

class SEDiscordRestart(Exception):
    """Used for restarting the bot"""

class SEDiscordExit(Exception):
    """Same thing as SEDiscordRestart, except it shuts down the bot"""

class PolicyEntry:
    """A single policy key. type can be 'bool', 'int', 'array', or 'str'."""
    def __init__(self, vtype, protected=False):
        self.type = vtype
        self.protected = protected
        self.value = None

    def set(self, value):
        """Checks value for errors and sets it"""
        global CACHE_UPDATED
        if (self.vtype == "bool") or (self.vtype == "int"):
            value = int(value)
        if self.vtype == "bool":
            if not((value == 0) or (value == 1)):
                raise ValueError("Invalid value for bool PolicyEntry")
        self.value = value
        CACHE_UPDATED = True


class Policy:
    """A Policy to make use easier"""
    def __init__(self):
        self.server_admin_required = PolicyEntry("bool")
        self.verify_enabled = PolicyEntry("bool")
        self.verify_check_report = PolicyEntry("bool")
        self.verify_check_rep = PolicyEntry("bool")
        self.verify_min_rep = PolicyEntry("int")
        self.server_password_enabled = PolicyEntry("bool")
        self.server_password = PolicyEntry("str", protected=True)

    @staticmethod
    def get(name):
        """Get Policy by name"""
        if name in cached_policies:
            return cached_policies[name]
        else:
            with open(f"data/policies/{name}", "rb") as f:
                policy = pickle.load(f)
                while len(cached_policies) >= MAX_POLICY_CACHE:
                    cached_policies.pop(random.choice(cached_policies))
                cached_policies[name] = policy
                return policy

class SEUser:
    """Represents a user, argument is self explanatory"""
    def __init__(self, discord_id):
        self.discord_id = discord_id
        c = db.cursor()
        c.execute("SELECT * FROM seusers WHERE discord_id=?", (self.id,))
        self.db_entry = c.fetchone()
        self.sename = self.db_entry[1]
        self.groups = self.db_entry[2].split(",")

    @staticmethod
    def get(discord_id):
        """Load SEUser from discord id (as a str)"""
        if str(discord_id) in cached_users:
            return cached_users[str(discord_id)]
        else:
            pass #TODO this

    @staticmethod
    def get_user_groups(discord_id=None, sename=None):
        """Return a user's groups. Can be called via their discord id or their SEDiscord id."""
        if discord_id != None:
            if str(discord_id) in cached_users:
                return cached_users[str(discord_id)].groups
            else:

def write_cache():
    for i in cached_policies:
        with open(f"data/policies/{i}", "wb") as f:
            pickle.dump(cached_policies[i], f)

def cache_auto_writer():
    while True:
        if CACHE_UPDATED:
            write_cache()
        time.sleep(0.5)

@bot.command()
async def glsetup(ctx):
    global db
    if not os.path.isdir("data"):
        await ctx.send("Creating data folders...")
        os.mkdir("data")
        await ctx.send("Created `data` directory")
        os.mkdir("data/policies")
        await ctx.send("Created `data/policies` directory")
        os.mkdir("data/profiles")
        await ctx.send("Created `data/profiles` directory")
        await ctx.send("Creating sqlite3 database...")
        db = sqlite3.connect("data/sediscord.db")
        await ctx.send("Created sqlite3 database")
        await ctx.send("Creating sqlite3 database tables...")
        c = db.cursor()
        c.execute("CREATE TABLE seusers (discord_id text, se_user text, se_groups text)")
        c.execute("CREATE TABLE policies (id text, creator text)")
        c.execute("CREATE TABLE servers (id text, se_server text, policy text)")
        c.execute("CREATE TABLE groups (name text, owner text)")
        await ctx.send("Created sqlite3 database tables")
        await ctx.send("Creating root_g SEGroup...")
        c.execute("INSERT INTO groups VALUES ('root_g', 'root_u')")
        await ctx.send("Creating root_u SEUser...")
        c.execute("INSERT INTO seusers VALUES (?, 'root_u', 'root_g,')", (ctx.author.id,))
        await ctx.send("Created root_u user and root_g group!")
        db.commit()
        await ctx.send("Creating DEFAULT_p policy...")
        policy = Policy()
        with open("data/policies/DEFAULT_p", "wb") as f:
            pickle.dump(policy, f)
        await ctx.send("Created DEFAULT_p policy!")
        await ctx.send("Setup finished!")
    else:
        await ctx.send("SEDiscord has already been set up.")

@bot.command()
async def restart():

def main():
    global cached_policies, cached_users
    try:
        cache_writer_thread = threading.Thread(target=cache_auto_writer, name="cache_writer_thread")
        cache_writer_thread.start()
        bot.run(sys.argv[1])
    except SEDiscordRestart:
        write_cache()
        cached_users = {}
        cached_policies = {}
        main()

main()