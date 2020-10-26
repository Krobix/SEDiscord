#!/usr/bin/env python3
from discord.ext import commands
import sys
import os
import asyncio
import secrets
import sqlite3
import pickle

bot = commands.Bot(command_prefix="se.")

#Setup sqlite3 db
if os.path.isdir("data"):
    db = sqlite3.connect("data/sediscord.db")

class PolicyEntry:
    """A single policy key. type can be 'bool', 'int', 'array', or 'str'."""
    def __init__(self, type, protected=False):
        self.type = type
        self.protected = protected
        self.value = None

class Policy:
    def __init__(self):
        self.server_admin_required = PolicyEntry("bool")
        self.verify_enabled = PolicyEntry("bool")
        self.verify_check_troll = PolicyEntry("bool")
        self.verify_check_rep = PolicyEntry("bool")
        self.verify_min_rep = PolicyEntry("int")
        self.server_password_enabled = PolicyEntry("bool")
        self.server_password = PolicyEntry("str", protected=True)

@bot.command()
async def glsetup(ctx):
    global db
    if not os.path.isdir("data"):
        ctx.send("Creating data folders...")
        os.mkdir("data")
        ctx.send("Created `data` directory")
        os.mkdir("data/srv")
        ctx.send("Created `data/srv` directory")
        os.mkdir("data/policies")
        ctx.send("Created `data/policies` directory")
        os.mkdir("data/profiles")
        ctx.send("Created `data/profiles` directory")
        ctx.send("Creating sqlite3 database...")
        db = sqlite3.connect("data/sediscord.db")
        ctx.send("Created sqlite3 database")
        ctx.send("Creating sqlite3 database tables...")
        c = db.cursor()
        c.execute("CREATE TABLE seusers (discord_id text, se_user text, se_groups text)")
        c.execute("CREATE TABLE policies (id text, creator text)")
        c.execute("CREATE TABLE servers (id text, se_server text, policy text)")
        c.execute("CREATE TABLE groups (name text, owner text)")
        ctx.send("Created sqlite3 database tables")
        ctx.send("Creating root_g SEGroup...")
        c.execute("INSERT INTO groups VALUES ('root_g', 'root_u')")
        ctx.send("Creating root_u SEUser...")
        c.execute("INSERT INTO seusers VALUES (?, 'root_u', 'root_g,')", (ctx.author.id))
        ctx.send("Created root_u user and root_g group!")
        db.commit()
        ctx.send("Creating DEFAULT_p policy...")
        policy = Policy()
        with open("data/policies/DEFAULT_p", "wb") as f:
            pickle.dump(policy, f)
        ctx.send("Created DEFAULT_p policy!")
        ctx.send("Setup finished!")

