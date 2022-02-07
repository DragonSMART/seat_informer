from mysql.connector import connect, Error
import configparser

config_bot = configparser.ConfigParser()
config_bot.read('botconfig.conf')


class MainDatabase:

    def __init__(self):
        self.host = config_bot['DEFAULT']['mysql_host']
        self.user = config_bot['DEFAULT']['mysql_user']
        self.password = config_bot['DEFAULT']['mysql_password']
        self.database = config_bot['DEFAULT']['mysql_database']
        self.connection = None
        self.init_database()


    def init_database(self):
        try:
            self.connection = connect(host=self.host, user=self.user, password=self.password, database=self.database)
        except Error as err:
            print(err)

    def get_cursor(self):
        if not self.connection.is_connected():
            return self.init_database()
        return self.connection.cursor()

    def get_alliance_paps(self, time_period):
        sql_select = '''
            SELECT
                corporation_infos.name, count(*) as amout
            FROM
                kassie_calendar_paps, corporation_members, corporation_infos
            WHERE
                kassie_calendar_paps.join_time LIKE %s and
                corporation_members.character_id = kassie_calendar_paps.character_id and
                corporation_members.corporation_id = corporation_infos.corporation_id and
                corporation_infos.alliance_id = 99007203
            GROUP BY corporation_infos.name
            ORDER BY amout DESC
            '''
        cursor = self.get_cursor()
        cursor.execute(sql_select, (time_period + '%',))
        rez = cursor.fetchall()
        cursor.close()
        return rez

    def get_corp_paps(self, corp_id, time_period):
        sql_select = '''
            SELECT
                character_infos.character_id, character_infos.name, count(*) as amout
            FROM
                kassie_calendar_paps, character_infos, corporation_members, corporation_infos
            WHERE
                kassie_calendar_paps.join_time LIKE %s and
                kassie_calendar_paps.character_id = character_infos.character_id and
                corporation_members.character_id = kassie_calendar_paps.character_id and
                corporation_members.corporation_id = corporation_infos.corporation_id and
                corporation_infos.corporation_id = %s
            GROUP BY character_infos.name
            ORDER BY amout DESC
            LIMIT 20
            '''
        cursor = self.get_cursor()
        cursor.execute(sql_select, (time_period + '%', corp_id))
        rez = cursor.fetchall()
        cursor.close()
        return rez

    def get_pilot_pap_tag(self, char_id, time_period):
        sql_select = '''
            SELECT
                calendar_tags.name, count(*)
            FROM
                kassie_calendar_paps, calendar_tags, calendar_tag_operation
            WHERE
                kassie_calendar_paps.join_time LIKE %s and
                kassie_calendar_paps.operation_id = calendar_tag_operation.operation_id and
                calendar_tag_operation.tag_id = calendar_tags.id and
                kassie_calendar_paps.character_id = %s
            GROUP BY calendar_tags.name
            '''
        cursor = self.get_cursor()
        cursor.execute(sql_select, (time_period + '%', char_id))
        rez = cursor.fetchall()
        cursor.close()
        return rez

    def get_pilot_pap_all(self, char_id, time_period):
        sql_select = '''
            SELECT count(*)
            FROM kassie_calendar_paps
            WHERE
                kassie_calendar_paps.join_time LIKE %s and
                kassie_calendar_paps.character_id = %s
            '''
        cursor = self.get_cursor()
        cursor.execute(sql_select, (time_period + '%', char_id))
        rez = cursor.fetchall()
        cursor.close()
        return rez

    def get_alliance_corp(self):
        sql_select = '''
            SELECT corporation_infos.corporation_id, corporation_infos.name
            FROM corporation_infos
            WHERE corporation_infos.alliance_id = 99007203
            '''
        cursor = self.get_cursor()
        cursor.execute(sql_select)
        rez = cursor.fetchall()
        cursor.close()
        return rez

    def get_linked_char(self, discord_id):
        sql_select = '''
            SELECT character_infos.character_id, character_infos.name
            FROM seat_connector_users, refresh_tokens, character_infos
            WHERE
                seat_connector_users.connector_id = %s and
                seat_connector_users.user_id = refresh_tokens.user_id and
                refresh_tokens.character_id = character_infos.character_id
            '''
        cursor = self.get_cursor()
        cursor.execute(sql_select, (discord_id,))
        rez = cursor.fetchall()
        cursor.close()
        return rez

    def get_pap_tag(self):
        sql_select = '''
            SELECT * FROM calendar_tags
        '''
        cursor = self.get_cursor()
        cursor.execute(sql_select)
        rez = cursor.fetchall()
        cursor.close()
        return rez