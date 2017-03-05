import sopel.module

@sopel.module.commands('modules')
def modules(bot, trigger):
    bot.reply(bot.config.core.enable)
