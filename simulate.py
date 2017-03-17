import sopel.module
import random
import time

launched = -1

@sopel.module.event('KICK')
@sopel.module.rule(r'.*')
def bampersand(bot, trigger):
    if trigger.args[1] == bot.nick:
        bot.quit('APOLLO')

@sopel.module.interval(3)
def start(bot):
    global launched
    launched = launched + 1

    if launched == 1:
        if len(bot.channels[bot.config.core.channels[0]].users) == 0:
            bot.msg(bot.config.core.channels[0], 'No users sad')
            launched = -1

        random.seed()
        while True:
            roll = random.randint(4, 8)
            time.sleep(roll)
            if simulate(bot):
                break
#        bot.msg(bot.config.core.channels[0], str(roll))

def shutdown(bot):
    bot.quit('APOLLO')

def simulate(bot):
    roll = random.randint(1, 100)
#    bot.msg(bot.config.core.channels[0], str(roll))
    if roll < 15:
        timeout()
        return True
    elif roll < 65:
        slap(bot, random.choice(list(bot.channels[bot.config.core.channels[0]].users.keys())), random.choice(list(bot.channels[bot.config.core.channels[0]].users.keys())))
    else:
        sandwich(bot, random.choice(list(bot.channels[bot.config.core.channels[0]].users.keys())))
    
    return False

def slap(bot, source, target):
    bot.msg(bot.config.core.channels[0], '{} slaps {}'.format(source, target))

def sandwich(bot, target):
    bot.msg(bot.config.core.channels[0], 'here you go {} [SANDWICH]'.format(target))

def timeout():
    sopel.irc.Bot.write = superwrite

def superwrite(self, args, text=None):
    return
