import sopel.module

@sopel.module.commands('modules')
def modules(bot, trigger):
    if trigger.group(3) == 'help':
        bot.say('admin and adminchannel are built in, all others have !module help available')
    else:
        bot.say('Modules loaded: ' + ', '.join(bot.config.core.enable))
