import sopel.module
import sqlite3
import collections
from datetime import datetime

helptext = collections.namedtuple('HelpText', 'perms command line')

class CronSection(sopel.config.types.StaticSection):
    user_min_interval = sopel.config.types.ValidatedAttribute('user_min_interval', int, default=900)
    admin_min_interval = sopel.config.types.ValidatedAttribute('admin_min_interval', int, default=60)
    user_max_crons = sopel.config.types.ValidatedAttribute('user_max_crons', int, default=1)
    admin_max_crons = sopel.config.types.ValidatedAttribute('admin_max_crons', int, default=3)

def configure(config):
    config.define_section('cron', CronSection)
    config.cron.configure_setting('user_min_interval', 'Minimum interval in seconds for user cronjobs')
    config.cron.configure_setting('admin_min_interval', 'Minimum interval in seconds for admin cronjobs')
    config.cron.configure_setting('user_max_cronx', 'Maximum cron jobs for users')
    config.cron.configure_setting('admin_max_crons', 'Maximum cron jobs for admins')

def setup(bot):
    bot.config.define_section('cron', CronSection)
    try:
        bot.db.execute('SELECT * FROM crontab')
    except:
        bot.db.execute(
                'CREATE TABLE crontab '
                '(id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'owner STRING, '
                'target STRING, '
                'interval INTEGER, '
                'lastrun DATETIME, '
                'nextrun DATETIME, '
                'mode STRING, '
                'text STRING)'
        )

    sqlite3.register_adapter(datetime, datetime2str)
    sqlite3.register_converter('DATETIME', str2datetime)

    if not bot.memory.contains('help'):
        bot.memory = sopel.tools.SopelMemory()
    
    bot.memory['help']['cron'] = sopel.tools.SopelMemory()
    bot.memory['help']['cron']['short'] = 'Runs commands at intervals'
    bot.memory['help']['cron']['long'] = {
            helptext('all', '!cron add <interval> msg|action <target> <text>', 'Adds a task to crontab'),
            helptext('all', '!cron del <id>', 'Removes a task from crontab'),
            helptext('all', '!cron list', 'Lists your cronjobs'),
            helptext('all', '!cron list all', 'Lists all cronjobs'),
            helptext('all', '!cron list <nick>', 'Lists cronjobs for specified nick')
            }

def datetime2str(val):
    return datetime(val).strftime('%Y-%m-%d %H:%M:%S')

def str2datetime(val):
    return datetime.strptime(str(val), '%Y-%m-%d %H:%M:%S')

@sopel.module.interval(60)
def crontab(bot):
    if not bot.say:
        return

    try:
        rows = bot.db.execute(
                'SELECT id, target, interval, nextrun, mode, text '
                'FROM crontab '
                'WHERE nextrun < DATETIME(\'now\', \'+59 seconds\') AND enabled = 1')
        for row in rows:
            if str2datetime(row[3]) < datetime.now():
                runjob(bot, row[0], row[1], row[2], row[4], row[5])
            else:
                threading.Timer((str2datetime(row[3]) - now).total_seconds(), runjob, [bot, row[0], row[1], row[2], row[4], row[5]])
    except:
        pass

def runjob(bot, id, target, interval, mode, text):
    if mode == 'msg':
        bot.msg(target, text)
    elif mode == 'action':
        bot.msg(target, '\x01ACTION {}\x01'.format(text))
    else:
        try:
            bot.db.execute(
                    'UPDATE crontab '
                    'SET enabled = 0 '
                    'WHERE id = ?',
                    [id])
        except:
            pass
        return

    try:
        bot.db.execute(
                'UPDATE crontab '
                'SET lastrun = datetime(\'now\'), '
                'nextrun = datetime(\'now\', ?) '
                'WHERE id = ?',
                ['+{} seconds'.format(interval), id])
    except:
        pass

@sopel.module.commands('cron')
def cron(bot, trigger):
    action = trigger.group(3)

    if action == 'add':
        try:
            _, interval, mode, target, text = trigger.group(2).split(' ', 4)
            interval = int(interval)
        except:
            bot.say('Usage: !cron add <interval> <mode> <target> <text>')
            return
        
        if trigger.is_privmsg:
            bot.say('Do it in the channel I dare you')
            return

        cronadd(bot, trigger.admin, trigger.nick, interval, mode, target, text)
    elif action == 'del':
        crondel(bot, trigger.admin, trigger.nick, trigger.group(4))
    elif action == 'list':
        cronlist(bot, trigger.nick, trigger.group(4))

def cronadd(bot, admin, nick, interval, mode, target, text):
    if interval < 1:
        bot.say('I\'m not sure why you thought that would work')
    if admin and interval < bot.config.cron.admin_min_interval:
        bot.say('Minimum interval for admins is {} seconds'.format(str(bot.config.cron.admin_min_interval)))
        return
    if not admin and interval < bot.config.cron.user_min_interval:
        bot.say('Minimum interval for users is {} seconds'.format(str(bot.config.cron.user_min_interval)))
        return
    if not mode in ('msg', 'action'):
        bot.say('Mode must be one of msg or action')
        return

    try:
        count = bot.db.execute(
                'SELECT COUNT(*) '
                'FROM crontab '
                'WHERE owner = ? AND enabled = 1 '
                'GROUP BY owner',
                [nick.lower()]).fetchone() or 0
        if count != 0:
            count = count[0]
        if admin and count >= bot.config.cron.admin_max_crons:
            bot.say('Max cronjobs for admins is {}'.format(str(bot.config.cron.admin_max_crons)))
            return
        if not admin and count >= bot.config.cron.user_max_crons:
            bot.say('Max cronjobs for users is {}'.format(str(bot.config.cron.user_max_crons)))
            return

        bot.db.execute(
                'INSERT INTO crontab (owner, target, interval, lastrun, nextrun, mode, text)'
                'VALUES (?, ?, ?, datetime(\'now\'), datetime(\'now\', ?), ?, ?)',
                [nick.lower(), target, interval, '+{} seconds'.format(interval), mode, text])
        row = bot.db.execute(
                'SELECT id, nextrun '
                'FROM crontab '
                'WHERE enabled = 1 '
                'ORDER BY id DESC '
                'LIMIT 1').fetchone()
        bot.say('Cronjob registered, ID: {}, next run: {}'.format(row[0], row[1]))
    except:
        bot.say('Error adding cron')

def crondel(bot, admin, nick, id):
    try:
        row = bot.db.execute(
                'SELECT owner '
                'FROM crontab '
                'WHERE id = ? AND enabled = 1',
                [id]).fetchone()
        if row == None:
            bot.say('Cannot delete cronjob with id {}'.format(id))
            return
        if not admin:
            if row != nick.lower():
                bot.say('Permission denied')
                return
        bot.db.execute(
                'UPDATE crontab '
                'SET enabled = 0 '
                'WHERE id = ?',
                [id])
        bot.say('Deleted cronjob with id {}'.format(id))
    except:
        bot.say('Cannot delete cronjob with id {}'.format(id))

def cronlist(bot, user_nick, command_nick):
    rows = None
    try:
        if not command_nick:
            rows = bot.db.execute(
                    'SELECT id, owner, target, interval, lastrun, nextrun, mode, text '
                    'FROM crontab '
                    'WHERE owner = ? AND enabled = 1',
                    [user_nick.lower()])
        elif command_nick == 'all':
            rows = bot.db.execute(
                    'SELECT id, owner, target, interval, lastrun, nextrun, mode, text '
                    'FROM crontab '
                    'WHERE enabled = 1')
        else:
            rows = bot.db.execute(
                    'SELECT id, owner, target, interval, lastrun, nextrun, mode, text '
                    'FROM crontab '
                    'WHERE owner = ? AND enabled = 1',
                    [command_nick.lower()])
    except:
        bot.say('Couldn\'t get cronjobs')
    
    if rows != None:
        for row in rows:
            bot.say('{} ({}): /{} {} {}, every {} seconds, last ran: {}, next run: {}'.format(
                    row[1],
                    row[0],
                    'me' if row[6] == 'action' else 'msg',
                    row[2],
                    row[7],
                    row[3],
                    row[4],
                    row[5]))

