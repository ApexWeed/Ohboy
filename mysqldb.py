import sopel.module
import mysql.connector
import json

from sopel.logger import get_logger

LOGGER = get_logger(__name__)

class MySQLSection(sopel.config.types.StaticSection):
    host = sopel.config.types.ValidatedAttribute('host')
    user = sopel.config.types.ValidatedAttribute('user')
    password = sopel.config.types.ValidatedAttribute('password')
    database = sopel.config.types.ValidatedAttribute('database')

def configure(config):
    config.define_section('mysql', MySQLSection)
    config.mysql.configure_setting('host', 'Host for MySQL database')
    config.mysql.configure_setting('user', 'User for MySQL database')
    config.mysql.configure_setting('password', 'Password for MySQL database')
    config.mysql.configure_setting('database', 'Database for MySQL database')

def setup(bot):
    bot.config.define_section('mysql', MySQLSection)

    db = MySQLDB(bot.config)
    #bot.db = db

@sopel.module.commands('mysql')
def command(bot, trigger):
    if not trigger.admin:
        return

    if trigger.group(3) == 'load' and trigger.owner:
        load(bot)
        bot.notice('MYSQL DB loaded', trigger.nick)
    elif trigger.group(3) == 'unload':
        unload(bot)
        bot.notice('SQLite DB loaded', trigger.nick)
    else:
        if isinstance(bot.db, MySQLDB):
            bot.notice('DB: MySQL')
        elif isinstance(bot.db, sopel.db.SopelDB):
            bot.notice('DB: SQLite3')
        else: 
            bot.notice('DB: {}'.format(str(type(bot.db))))

def load(bot):
    db = MySQLDB(bot.config)
    bot.db = db

def unload(bot):
    db = sopel.db.SopelDB(bot.config)
    bot.db = db

class MySQLDB(object):
    def __init__(self, config):
        self.host = config.mysql.host
        self.user = config.mysql.user
        self.password = config.mysql.password
        self.database = config.mysql.database

        self._create()

    def connect(self, autocommit = True):
        return mysql.connector.connect(host = self.host, user = self.user, password = self.password, database = self.database, autocommit = autocommit)

    def execute(self, *args, **kwargs):
        # Backwards compatibility.
        if '?' in args[0]:
            args = list(args)
            args[0] = args[0].replace('?', '%s')
        conn = self.connect()
        cur = conn.cursor(buffered = True)
        cur.execute(*args, **kwargs)
        return cur

    def _create(self):
        try:
            self.execute('SELECT * FROM nick_ids')
            self.execute('SELECT * FROM nicknames')
            self.execute('SELECT * FROM nick_values')
            self.execute('SELECT * FROM channel_values')
        except:
            pass
        else:
            return

        self.execute('CREATE TABLE IF NOT EXISTS nick_ids '
                '(nick_id INT NOT NULL AUTO_INCREMENT, PRIMARY KEY(nick_id))')
        self.execute('CREATE TABLE IF NOT EXISTS nicknames '
                '(nick_id INT REFERENCES nick_ids(nick_id), '
                'slug VARCHAR(255), canonical VARCHAR(255), PRIMARY KEY(slug))')
        self.execute('CREATE TABLE IF NOT EXISTS nick_values '
                '(nick_id INT REFERENCES nick_ids(nick_id), '
                '`key` VARCHAR(255), value TEXT, '
                'PRIMARY KEY(nick_id, `key`))')
        self.execute('CREATE TABLE IF NOT EXISTS channel_values '
                '(channel VARCHAR(255), `key` VARCHAR(255), value TEXT, '
                'PRIMARY KEY(channel, `key`))')

    def get_uri(self):
        return 'mysql://{}:{}@{}/{}'.format(self.user, self.password, self.host, self.database)

    # Nick functions.

    def get_nick_id(self, nick, create = True):
        slug = nick.lower()
        nick_id = self.execute('SELECT nick_id FROM nicknames WHERE slug = %s', [slug]).fetchone()

        if nick_id is None:
            if not create:
                raise ValueError('No ID exists for the given nick')
            conn = self.connect(autocommit = False)
            cur = conn.cursor(buffered = True)
            cur.execute('INSERT INTO nick_ids VALUES (NULL)')
            nick_id = cur.lastrowid
            cur.execute('INSERT INTO nicknames (nick_id, slug, canonical) VALUES (%s, %s, %s)',
                    [nick_id, slug, str(nick)])
            conn.commit()
            cur.execute('SELECT nick_id FROM nicknames WHERE slug = %s', [slug])
            nick_id = cur.fetchone()

        return nick_id[0]

    def alias_nick(self, nick, alias):
        nick = sopel.tools.Identifier(nick)
        alias = sopel.tools.Identifier(nick)
        nick_id = self.get_nick_id(nick)
        try:
            self.execute('INSERT INTO nicknames (nick_id, slug, canonical) VALUES (%s, %s, %s)',
                    [nick_id, alias.lower(), alias])
        except mysql.connector.IntegrityError:
            raise ValueError('Alias alreay exists.')

    def set_nick_value(self, nick, key, value):
        nick = sopel.tools.Identifier(nick)
        value = json.dumps(value, ensure_ascii = False)
        nick_id = self.get_nick_id(nick)
        self.execute('REPLACE INTO nick_values VALUE (%s, %s, %s)',
                [nick_id, key, value])

    def get_nick_value(self, nick, key):
        nick = sopel.tools.Identifier(nick)
        result = self.execute('SELECT value FROM nicknames JOIN nick_values '
                'ON nicknames.nick_id = nick_values.nick_id '
                'WHERE slug = %s AND `key` = %s',
                [nick.lower(), key]).fetchone()
        if result is None:
            return result
        return json.loads(result[0].decode('utf-8'))

    def unalias_nick(self, alias):
        alias = sopel.tools.Identifier(alias)
        nick_id = self.get_nick_id(alias, False)
        count = self.execute('SELECT COUNT(*) FROM nicknames WHERE nick_id = %s',
                [nick_id]).fetchone()[0]

        if count <= 1:
            raise ValueError('Given alias is the only entry in its group.')
        self.execute('DELETE FROM nicknames WHERE slug = %s', [alias.lower()])

    def delete_nick_group(self, nick):
        nick = sopel.tools.Identifier(nick)
        nick_id = self.get_nick_id(nick, False)
        conn = self.connect(autocommit = False)
        cur = conn.cursor(buffered = True)
        cur.execute('DELETE FROM nicknames WHERE nick_id = %s', [nick_id])
        cur.execute('DELETE FROM nick_values WHERE nick_id = %s', [nick_id])
        conn.commit()

    def merge_nick_groups(self, first_nick, second_nick):
        first_id = self.get_nick_id(sopel.tools.Identifier(first_nick))
        second_id = self.get_nick_id(sopel.tools.Identifier(second_nick))
        conn = self.connect(autocommit = False)
        cur = conn.cursor(buffered = True)
        cur.execute('UPDATE OR IGNORE nick_values SET nick_id = %s WHERE nick_id = %s',
                [first_id, second_id])
        cur.execute('DELETE FROM nick_values WHERE nick_id = %s', [second_id])
        cur.execute('UPDATE nicknames SET nick_id = %s WHERE nick_id = %s'
                [first_id, second_id])
        conn.commit()

    # Channel functions.

    def set_channel_value(self, channel, key, value):
        channel = sopel.tools.Identifier(channel).lower()
        value = json.dumps(value, ensure_ascii = False)
        self.execute('REPLACE INTO channel_values VALUES (%s, %s, %s)',
                [channel, key, value])

    def get_channel_value(self, channel, key):
        channel = sopel.tools.Identifier(channel).lower()
        result = self.execute('SELECT value FROM channel_values WHERE channel = %s AND `key` = %s',
                [channel, key]).fetchone()
        if result is None:
            return result

        return json.loads(result[0].decode('utf-8'))

    # Channel or nick functions.

    def get_nick_or_channel_value(self, name, key):
        name = sopel.tools.Identifier(name)
        if name.is_nick():
            return self.get_nick_value(name, key)
        else:
            return self.get_channel_value(name, key)

    def get_preferred_value(self, names, key):
        for name in names:
            value = self.get_nick_or_channel_value(name, key)
            if value is not None:
                return value
