import sopel.module
import sys

if sys.version_info.major >= 3:
    unicode = str
    basestring = str

def _deserialize(value):
    if value is None:
        return None
    # sqlite likes to return ints for strings that look like ints, even though
    # the column type is string. That's how you do dynamic typing wrong.
    value = unicode(value)
    # Just in case someone's mucking with the DB in a way we can't account for,
    # ignore json parsing errors
    try:
        value = json.loads(value)
    except:
        pass
    return value

@sopel.module.commands('activity')
def help(bot, trigger):
    if trigger.group(3) == 'help':
        bot.say('Logs word and line counts, !stats <nick> for per nick stats, !stats for global stats.')

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
        bot.say('Stats for ' + trigger.group(3) + ': words: ' + str(wc) + ', lines: ' + str(lc))
    else:
        wc = 0
        wcs = bot.db.execute(
                'SELECT value FROM nick_values '
                'WHERE key = ?',
                ['wc']).fetchall()
        for row in wcs:
            #bot.say(str(row))
            wc += row[0]
        lc = 0
        lcs = bot.db.execute(
                'SELECT value FROM nick_values '
                'WHERE key = ?',
                ['lc']).fetchall()
        for row in lcs:
            #bot.say(str(row))
            lc += row[0]
    
        bot.say('Global stats: words: ' + str(wc) + ', lines: ' + str(lc))
