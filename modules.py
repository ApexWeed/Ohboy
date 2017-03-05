import sopel.module

@sopel.module.commands('modules')
def modules(bot, trigger):
    bot.say('Modules loaded: ' + ', '.join(bot.config.core.enable))
