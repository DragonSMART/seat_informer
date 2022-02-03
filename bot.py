import discord
import configparser
import database
import datetime


class DiscordBot(discord.Client):
    def __init__(self):
        super().__init__()
        self.command_prefix = '!'
        self.database = database.MainDatabase()

    async def on_ready(self):
        print('Bot starting!')

    async def on_message(self, message):
        if not message.content.startswith(self.command_prefix) or len(message.content) == 1:
            return
        channel = message.channel
        author = message.author
        command = message.content.split(' ')[0].lower()
        message_text = message.content[len(command) + 1::]

        if command == '!pap':
            await self.get_pap(message, message_text)

    async def get_pap(self, message, message_text):
        if message_text == '':
            time_period = datetime.datetime.utcnow().strftime("%Y-%m")
        else:
            time_period = message_text
        all_paps = self.database.get_paps(time_period)
        top_message = '```diff\n'
        bottom_message = '''```'''
        post_message = ''
        for one_pap in all_paps:
            corp_name = one_pap[0]
            amount_paps = one_pap[1]
            post_message += '{corp_name: <25}|{amount: >5}\n'.format(corp_name=corp_name,
                                                                     amount=amount_paps)
        if len(post_message) == 0:
            return await message.channel.send('Крабы не воюют :)')
        return await message.channel.send(top_message + post_message + bottom_message)


if __name__ == '__main__':
    config_bot = configparser.ConfigParser()
    config_bot.read('botconfig.conf')

    bot_token = config_bot['DEFAULT']['bot_token']
    bot = DiscordBot()
    bot.run(bot_token)
