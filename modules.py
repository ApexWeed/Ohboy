import sopel.module

@sopel.module.commands('modules')
def modules(bot, trigger):
    if trigger.group(3) == 'help':
        bot.say('find, admin and adminchannel are built in, reload, and op are admin only, all others have \'!<module> help\' available')
    else:
        bot.say('Modules loaded: ' + ', '.join(bot.config.core.enable))
