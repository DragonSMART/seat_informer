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
        print(f'Bot starting! {self.user}')

    async def on_message(self, message):
        if not message.content.startswith(self.command_prefix) or len(message.content) == 1:
            return
        channel = message.channel
        author = message.author
        command = message.content.split(' ')[0].lower()
        message_text = message.content[len(command) + 1::]

        if command == '!papcorp' and await self.check_access(message):
            await self.get_alliance_paps(message, message_text)
        elif command == '!pappilot' and await self.check_access(message):
            await self.get_corp_paps(message, message_text)
        elif command == '!pap' and await self.check_access(message):
            await self.get_pilot_paps(message, message_text)
        elif command == '!papfc' and await self.check_access(message):
            await self.get_papfc(message, message_text)
        elif command == '!10' and await self.check_access(message):
            await self.get_ten(message, message_text)


    async def get_alliance_paps(self, message, message_text):
        if message_text == '':
            time_period = datetime.datetime.utcnow().strftime("%Y-%m")
        else:
            time_period = message_text
        all_paps = self.database.get_alliance_paps(time_period)
        top_message = '```diff\n'
        bottom_message = '''```'''
        post_message = ''
        all_tags_pap = await self.get_pap_tag()
        for one_pap in all_paps:
            corp_name = one_pap[1]
            total_paps = one_pap[2]
            post_message += '{corp_name: <25}|{total: >5}|'.format(corp_name=corp_name,
                                                                    total=total_paps)
            one_corp_paps = self.database.get_corp_paps_tag(corp_id=one_pap[0], time_period=time_period)
            detail_pap = all_tags_pap.copy()
            for one_corp_tag in one_corp_paps:
                detail_pap[one_corp_tag[0]] += one_corp_tag[1]
            for one_tag in detail_pap:
                post_message += f' {one_tag}: {detail_pap[one_tag]} '
            post_message += f'other: {total_paps - sum(detail_pap.values())}\n'

        if len(post_message) == 0:
            return await message.channel.send('Крабы не воюют :)')
        return await message.channel.send(top_message + post_message + bottom_message)

    async def get_corp_paps(self, message, message_text):
        extra_command = message_text.split(' ')
        need_corp_id = None
        need_corp_name = None

        if self.database.get_corp_ticker(corp_ticker=str(extra_command[0]).upper()):
            temp_corp_info = self.database.get_corp_ticker(corp_ticker=str(extra_command[0]).upper())
            need_corp_id = int(temp_corp_info[0])
            need_corp_name = temp_corp_info[1]

        if (message_text == '' and need_corp_id is None) or (need_corp_id and len(extra_command) == 1):
            time_period = datetime.datetime.utcnow().strftime("%Y-%m")
        elif need_corp_id and len(extra_command) == 2:
            time_period = extra_command[1]
        else:
            time_period = message_text

        bottom_message = '''```'''
        if need_corp_id:
            alliance_corps = {need_corp_id : need_corp_name}
        else:
            alliance_corps = await self.get_alliance_corp()
        all_tag_pap = await self.get_pap_tag()

        for one_corp_id, one_corp_name in alliance_corps.items():
            top_message = f'Corporation name: {one_corp_name}```diff\n'
            post_message = ''
            new_post_message = ''
            one_corp_paps = self.database.get_corp_paps_all(corp_id=one_corp_id, time_period=time_period)
            if not one_corp_paps:
                continue
            for one_pilot_pap in one_corp_paps:
                pilot_name = one_pilot_pap[1]
                total_paps = one_pilot_pap[2]
                new_post_message += '{pilot_name: <25}|{total: >3}|'.format(pilot_name=pilot_name,
                                                                        total=total_paps)
                detail_pap = all_tag_pap.copy()
                pilot_pap_tags = self.database.get_pilot_pap_tag(char_id=one_pilot_pap[0], time_period=time_period)
                for one_pilot_tag in pilot_pap_tags:
                    detail_pap[one_pilot_tag[0]] += one_pilot_tag[1]

                for one_detail_pap in detail_pap:
                    new_post_message += f' {one_detail_pap}: {detail_pap[one_detail_pap]} '
                new_post_message += f'other: {total_paps - sum(detail_pap.values())}\n'

                if len(post_message) + len(new_post_message) > 1800:
                    await message.channel.send(top_message + post_message + bottom_message)
                    post_message = new_post_message
                else:
                    post_message += new_post_message
                new_post_message = ''
            await message.channel.send(top_message + post_message + bottom_message)

    async def get_pilot_paps(self, message, message_text):
        if message_text == '':
            time_period = datetime.datetime.utcnow().strftime("%Y-%m")
        else:
            time_period = message_text

        top_message = f'Charaсter paps: ```diff'
        post_message = ''
        bottom_message = '''```'''

        all_chars = await self.get_linked_char(message)
        total = 0
        all_tag_pap = await self.get_pap_tag()

        for one_char in all_chars:
            detail_pap = all_tag_pap.copy()
            char_id = one_char
            char_name = all_chars[one_char]
            char_paps_tags = self.database.get_pilot_pap_tag(char_id=char_id, time_period=time_period)
            char_paps_all = self.database.get_pilot_pap_all(char_id=char_id, time_period=time_period)[0][0]
            if len(char_paps_tags) == 0:
                continue
            post_message += f'\n{char_name} | '
            for one_paps in char_paps_tags:
                detail_pap[one_paps[0]] += one_paps[1]
                post_message += f'{one_paps[0]}: {detail_pap[one_paps[0]]} '
            another_paps = char_paps_all - sum(detail_pap.values())
            if another_paps > 0:
                post_message += f'other: {char_paps_all - sum(detail_pap.values())}'
            total += char_paps_all
        if not str(message.channel).startswith('Direct Message with'):
            await message.delete()
        if len(post_message) == 0:
            return await message.author.send('Крабы не воюют :)')
        return await message.author.send(top_message + post_message + bottom_message + f'Total: {total}')

    async def get_papfc(self, message, message_text):
        if message_text == '':
            time_period = datetime.datetime.utcnow().strftime("%Y-%m")
        else:
            time_period = message_text

        top_message = '```diff'
        bottom_message = '''```'''
        post_message = ''

        all_papfc = self.database.get_fcpap_all(time_period=time_period)

        all_tag_pap = await self.get_pap_tag()
        for one_papfc in all_papfc:
            fc_name = one_papfc[1]
            total_paps = one_papfc[2]
            post_message += '\n{fc_name: <15} | {total_paps: >5} | '.format(fc_name=fc_name, total_paps=total_paps)
            detail_pap = all_tag_pap.copy()
            fcpap_tags = self.database.get_fcpap_tag(char_id=one_papfc[0], time_period=time_period)
            for one_fcpap_tag in fcpap_tags:
                detail_pap[one_fcpap_tag[0]] += one_fcpap_tag[1]
            for one_detail_pap in detail_pap:
                if detail_pap[one_detail_pap] > 0:
                    post_message += f'{one_detail_pap} : {detail_pap[one_detail_pap]} '
            other_pap = total_paps - sum(detail_pap.values())
            if other_pap > 0:
                post_message += f'other: {other_pap}'
        return await message.channel.send(top_message + post_message + bottom_message)

    async def get_alliance_corp(self):
        alliance_corps = self.database.get_alliance_corp()
        all_corp = {}
        for one_corp in alliance_corps:
            all_corp[one_corp[0]] = one_corp[1]
        return all_corp

    async def get_linked_char(self, message):
        author_id = message.author.id
        all_linked_char = self.database.get_linked_char(discord_id=author_id)
        linked_char = {}
        for one_char in all_linked_char:
            linked_char[one_char[0]] = one_char[1]
        return linked_char

    async def get_pap_tag(self):
        all_tag = self.database.get_pap_tag()
        tags = {}
        for one_tag in all_tag:
            tags[one_tag[1]] = 0
        return tags

    async def get_discord_user_role(self, message):
        discord_user_id = message.author.id
        temp_all_roles = self.database.get_discord_user_role(discord_id=discord_user_id)
        user_roles = []
        for one_role in temp_all_roles:
            user_roles.append(one_role[0])
        return user_roles

    async def check_access(self, message):
        command = message.content.split(' ')[0].lower()[1::]
        discord_user_id = message.author.id
        command_access = [one_role.strip().lower() for one_role in config_bot['COMMANDS'][command].split(',')]
        if 'all' in command_access:
            return True

        all_user_role = await self.get_discord_user_role(message)
        for one_role in all_user_role:
            if str(one_role).lower() in command_access:
                return True
        return False

    async def get_ten(self, message, message_text):
        if message_text == '':
            time_period = datetime.datetime.utcnow().strftime("%Y-%m")
        else:
            time_period = message_text

        post_message = ''

        all_charaster_ten = self.database.get_ten(time_period=time_period)
        summ_all_ten = sum([x for x in (one_charaster[1] for one_charaster in all_charaster_ten)])
        for one_charaster in all_charaster_ten:
            one_charaster_name = one_charaster[0]
            one_charaster_count = one_charaster[1]
            one_charaster_persent = round(one_charaster_count * 100 / summ_all_ten, 1)
            post_message += f'{one_charaster_name: <20} | {one_charaster_persent: >4}% |\n'
        channel = bot.get_channel(876816746575708170)
        await channel.send('```' + post_message + '```')


if __name__ == '__main__':
    config_bot = configparser.ConfigParser()
    config_bot.read('botconfig.conf')

    bot_token = config_bot['DEFAULT']['bot_token']
    bot = DiscordBot()
    bot.run(bot_token)
