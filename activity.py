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
            wpl = wc / lc
        else:
            wpl = 0
        bot.say('Stats for ' + trigger.group(3) + ': words: ' + str(wc) + ', lines: ' + str(lc) + ' words per line: ' + str(wpl))
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
            wpl = wc / lc
        else:
            wpl = 0
    
        bot.say('Global stats: words: ' + str(wc) + ', lines: ' + str(lc) + ' words per line: ' + str(wpl))
