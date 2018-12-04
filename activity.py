import sopel.module
import sys
import collections
import json

helptext = collections.namedtuple('HelpText', 'perms command line')

if sys.version_info.major >= 3:
    unicode = str
    basestring = str

def setup(bot):
    if not bot.memory.contains('help'):
        bot.memory['help'] = sopel.tools.SopelMemory()
    
    bot.memory['help']['activity'] = sopel.tools.SopelMemory()
    bot.memory['help']['activity']['short'] = 'Tracks activity statistics'
    bot.memory['help']['activity']['long'] = {
            helptext('all', '!stats', 'Lists channel stats'),
            helptext('all', '!stats <nick>', 'Lists stats for specified nick')
            }

@sopel.module.rule('^[^!](.*)')
def activity(bot, trigger):
    line_wc = len(trigger.group(1).split(' '))
    total_wc = bot.db.get_nick_value(trigger.nick, 'wc') or 0
    bot.db.set_nick_value(trigger.nick, 'wc', line_wc + total_wc)

    lc = bot.db.get_nick_value(trigger.nick, 'lc') or 0
    bot.db.set_nick_value(trigger.nick, 'lc', lc + 1)

@sopel.module.commands('stats')
def stats(bot, trigger):
    if trigger.group(2):
        wc = bot.db.get_nick_value(trigger.group(3), 'wc') or 0
        lc = bot.db.get_nick_value(trigger.group(3), 'lc') or 0
        if lc > 0:
            wpl = float(wc) / lc
        else:
            wpl = 0
        bot.say('Stats for {0}: words: {1}, lines: {2} words per line: {3:.3f}'.format(
            trigger.group(3), wc, lc, wpl))
    else:
        wc = bot.db.execute(
                'SELECT SUM(value) FROM nick_values '
                'WHERE `key` = ?',
                ['wc']).fetchone()[0]
        lc = bot.db.execute(
                'SELECT SUM(value) FROM nick_values '
                'WHERE `key` = ?',
                ['lc']).fetchone()[0]
        if lc > 0:
            wpl = float(wc) / lc
        else:
            wpl = 0
    
        bot.say('Global stats: words: {0}, lines: {1} words per line: {2:.3f}'.format(wc, lc, wpl))

@sopel.module.commands('top10')
def top10(bot, trigger):
    scores = bot.db.execute(
            'SELECT n.canonical, w.value, l.value '
            'FROM nicknames n '
            'INNER JOIN '
            '( '
            '   SELECT nick_id, value '
            '   FROM nick_values '
            '   WHERE key = ? '
            ')  w ON w.nick_id = n.nick_id '
            'INNER JOIN '
            '( '
            '   SELECT nick_id, value '
            '   FROM nick_values '
            '   WHERE key = ? '
            ') l ON l.nick_id = n.nick_id '
            'ORDER BY w.value DESC ',
            ['wc', 'lc']).fetchmany(10)

    bot.say(u'Top 10 stats: {0}'.format(u' : '.join(u'{0} - {1} w, {2} l, {3:.3f} wpl'.format(
        mangle(x[0]), x[1], x[2], 0 if x[2] == 0 else float(x[1]) / x[2]) for
        x in scores)))

def merge(bot, nick, alt):
    wco = bot.db.get_nick_value(nick, 'wc') or 0
    wcn = bot.db.get_nick_value(alt, 'wc') or 0
    lco = bot.db.get_nick_value(nick, 'lc') or 0
    lcn = bot.db.get_nick_value(alt, 'lc') or 0

    bot.db.set_nick_value(nick, 'wc', wco + wcn)
    bot.db.set_nick_value(nick, 'lc', lco + lcn)
    return "{0} words, {1} lines".format(wcn, lcn)

def mangle(nick):
    return u"{0}{1}{2}".format(nick[:1], unichr(int('200B', 16)), nick[1:])

