import sopel.modules

@sopel.module.rule(r'ping.*')
def pong(bot, trigger):
    bot.say('pong')

@sopel.module.rule(r'.*boob.*')
def boobs(bot, trigger):
    bot.action('jiggles')

@sopel.module.rule(r'^\.bang')
def bang(bot, trigger):
    bot.say('{} is a bad guy'.format(trigger.nick))
