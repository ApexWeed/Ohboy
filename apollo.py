import sopel.module
import collections

helptext = collections.namedtuple('HelpText', 'perms command line')

def setup(bot):
    if not bot.memory.contains('help'):
        bot.memory['help'] = sopel.tools.SopelMemory()

    bot.memory['help']['apollo'] = sopel.tools.SopelMemory()
    bot.memory['help']['apollo']['short'] = 'Feature parity with APOLLO'
    bot.memory['help']['apollo']['long'] = {
            helptext('all', '!sandwich', 'Requests a sandwich'),
            helptext('all', '!sudosandwich', 'Requests a sandwich'),
            helptext('all', '!slap <target>', 'Slaps somebody around'),
            helptext('admin', '!sudoslap <count> <target>', 'Slaps somebody around. A bunch')
            }

@sopel.module.commands('slap')
def slap(bot, trigger):
    if trigger.group(2):
        bot.say(trigger.nick + ' slaps ' + trigger.group(2))

@sopel.module.commands('sandwich')
def sandwich(bot, trigger):
    bot.say('Make it yourself, ' + trigger.nick)

@sopel.module.commands('sudosandwich')
def sudosandwich(bot, trigger):
    bot.say('Here you go, ' + trigger.nick + ' [sandwich]')

@sopel.module.commands('sudoslap')
def sudoslap(bot, trigger):
    if not trigger.admin or not trigger.group(3) or not trigger.group(4):
        return

    try:
        count = int(trigger.group(3))
    except:
        return

    for i in range(0, count):
        bot.say(trigger.nick + ' slaps ' + trigger.group(2)[len(trigger.group(3)) + 1:] + ', take ' + str(i + 1))
