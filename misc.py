import sopel.modules

@sopel.module.rule(r'ping.*')
def pong(bot, trigger):
    bot.say('pong')
