discord.py
==========

# Privacy Policy

Zapper takes your privacy seriously. To better protect your privacy we provide this privacy policy notice explaining the way your personal information is collected and used.


## Collection of Routine Information

This app tracks basic information about their users. This information includes, but is limited to, username, app details, timestamps and server modifications. None of this information can personally identify specific users to this app. The information is tracked for routine administration and maintenance purposes.


## Links to Third Party Websites

We have included links on this app for your use and reference. We are not responsible for the privacy policies on these websites. You should be aware that the privacy policies of these websites may differ from our own.


## Security

The security of your personal information is important to us, but remember that no method of transmission over the Internet, or method of electronic storage, is 100% secure. While we strive to use commercially acceptable means to protect your personal information.


## Changes To This Privacy PolicyThis Privacy Policy is effective as of 07/08/2024 and will remain in effect except with respect to any changes in its provisions in the future, which will be in effect immediately after being posted on this page.

We reserve the right to update or change our Privacy Policy at any time and you should check this Privacy Policy periodically. If we make any material changes to this Privacy Policy, we will notify you either through the a Discord Direct Message, or by placing a prominent notice on Discord Bot profile.


## Contact Information

For any questions or concerns regarding the privacy policy, please send us a message on discord to @aiecsis.



A modern, easy to use, feature-rich, and async ready API wrapper for Discord written in Python.

Key Features
-------------

- Modern Pythonic API using ``async`` and ``await``.
- Proper rate limit handling.
- Optimised in both speed and memory.

Installing
----------

**Python 3.8 or higher is required**

To install the library without full voice support, you can just run the following command:


    # Linux/macOS
    python3 -m pip install -U discord.py

    # Windows
    py -3 -m pip install -U discord.py

Otherwise to get voice support you should run the following command:

    # Linux/macOS
    python3 -m pip install -U "discord.py[voice]"

    # Windows
    py -3 -m pip install -U discord.py[voice]


To install the development version, do the following:


    $ git clone https://github.com/Rapptz/discord.py
    $ cd discord.py
    $ python3 -m pip install -U .[voice]


Optional Packages
~~~~~~~~~~~~~~~~~~

* `PyNaCl <https://pypi.org/project/PyNaCl/>`__ (for voice support)

Please note that when installing voice support on Linux, you must install the following packages via your favourite package manager (e.g. ``apt``, ``dnf``, etc) before running the above commands:

* libffi-dev (or ``libffi-devel`` on some systems)
* python-dev (e.g. ``python3.8-dev`` for Python 3.8)

~~~~~~~~~~~~~~~~~~

Quick Example

~~~~~~~~~~~~~~~~~~

    import discord

    class MyClient(discord.Client):
        async def on_ready(self):
            print('Logged on as', self.user)

        async def on_message(self, message):
            # don't respond to ourselves
            if message.author == self.user:
                return

            if message.content == 'ping':
                await message.channel.send('pong')

    intents = discord.Intents.default()
    intents.message_content = True
    client = MyClient(intents=intents)
    client.run('token')

~~~~~~~~~~~~~~~~~~

Bot Example

~~~~~~~~~~~~~

    import discord
    from discord.ext import commands

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='>', intents=intents)

    @bot.command()
    async def ping(ctx):
        await ctx.send('pong')

    bot.run('token')

~~~~~~~~~~~~~~~~~~

Links
------

- [Documentation](https://discordpy.readthedocs.io/en/latest/index.html>)
- [Official Discord Server](https://discord.gg/h8ngsYXzFa)
- [Discord API](https://discord.gg/discord-api>)
