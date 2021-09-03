import sqlite3
dbpath = './db/data.sqlite'
connection = sqlite3.connect(dbpath)
connection.isolation_level = None


class Database:
    def __init__(self):
        self.cursor = connection.cursor()

    def execute(self, sql):
        self.cursor.execute(sql)

    def setup(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS '
                            'channel_invite(guild_id integer, channel_id integer, role_id integer, invite_link)')

    def del_invite(self):
        self.cursor.execute('DROP TABLE channel_invite')
        return True

    def add_invite_link(self, guild_id: int, channel_id: int, role_id: int, invite_link: str):
        self.setup()
        self.cursor.execute('INSERT INTO channel_invite VALUES (?,?,?,?)', (guild_id, channel_id, role_id, invite_link))
        return True

    def del_invite_link(self, guild_id: int, channel_id: int):
        self.setup()
        self.cursor.execute('DELETE FROM channel_invite WHERE guild_id = ? AND channel_id = ?', (guild_id, channel_id))
        return True

    def update_invite_role(self, guild_id: int, channel_id: int, role_id: int):
        self.setup()
        self.cursor.execute('UPDATE channel_invite SET role_id = ? WHERE guild_id = ? AND channel_id = ?',
                            (role_id, guild_id, channel_id))
        return True

    def list_invite_link(self, guild_id: int):
        self.setup()
        res = self.cursor.execute('SELECT channel_id FROM channel_invite WHERE guild_id = ?',
                                  (guild_id,))
        data = res.fetchall()
        n_data = [i[0] for i in data]
        return n_data

    def get_invite_role(self, guild_id: int, channel_id: int):
        self.setup()
        res = self.cursor.execute('SELECT role_id FROM channel_invite WHERE guild_id = ? AND channel_id = ?',
                                  (guild_id, channel_id))
        data = res.fetchall()
        n_data = [i[0] for i in data]
        return n_data

    def all_invite_role(self, guild_id: int):
        self.setup()
        res = self.cursor.execute('SELECT role_id, channel_id, invite_link FROM channel_invite WHERE guild_id = ?',
                                  (guild_id,))
        data = res.fetchall()
        return data

    def fetch_invite_role(self, guild_id: int, invite_link: str):
        self.setup()
        res = self.cursor.execute('SELECT role_id FROM channel_invite WHERE guild_id = ? AND invite_link = ?',
                                  (guild_id, invite_link))
        data = res.fetchall()
        n_data = [i[0] for i in data]
        return n_data

