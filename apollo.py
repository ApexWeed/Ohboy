import sopel.module

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