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

    def get_paps(self, time_period):
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
        cursor = self.connection.cursor()
        cursor.execute(sql_select, (time_period + '%',))
        rez = cursor.fetchall()
        cursor.close()
        return rez

    def get_corp_paps(self, corp_id, time_period):
        sql_select = '''
            SELECT
                character_infos.name, count(*) as amout
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
            LIMIT 30
            '''
        cursor = self.connection.cursor()
        cursor.execute(sql_select, (time_period + '%', corp_id))
        rez = cursor.fetchall()
        cursor.close()
        return rez

    def get_alliance_corp(self):
        sql_select = '''
            SELECT corporation_infos.corporation_id, corporation_infos.name
            FROM corporation_infos
            WHERE corporation_infos.alliance_id = 99007203
            '''
        cursor = self.connection.cursor()
        cursor.execute(sql_select)
        rez = cursor.fetchall()
        cursor.close()
        return rez
