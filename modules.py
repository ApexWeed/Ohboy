import sopel.module
import collections

helptext = collections.namedtuple('HelpText', 'perms command line')

def setup(bot):
    if not bot.memory.contains('help'):
        bot.memory['help'] = sopel.tools.SopelMemory()

    bot.memory['help']['modules'] = sopel.tools.SopelMemory()
    bot.memory['help']['modules']['short'] = 'Lists enabled modules'
    bot.memory['help']['modules']['long'] = {
            helptext('all', '!modules', 'Lists enabled modules')
            }

@sopel.module.commands('modules')
def modules(bot, trigger):
    bot.say('Modules loaded: ' + ', '.join(bot.config.core.enable))
