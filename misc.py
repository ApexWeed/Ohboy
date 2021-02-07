from datetime import datetime
from dateutil import tz
import sopel.modules
import random

mario = False

def setup(bot):
    random.seed();

@sopel.module.rule(r'ping.*')
def pong(bot, trigger):
    bot.say('pong')

@sopel.module.rule(r'.*boob.*')
@sopel.module.rule(r'.*bewb.*')
@sopel.module.rule(r'.*tits.*')
def boobs(bot, trigger):
    if random.randint(1, 100) > 70:
        return
    bot.action('jiggles')

#@sopel.module.rule(r'.*ohboy.*')
def ohboy(bot, trigger):
    bot.say('Ohboy')

mash = ('Did you mean \x1D.bef\x1D {}?', '{} is a bad guy', '".bang" - {}, 2017', '{}\'s hobbies: banging ducks', 'I banged a duck and all I got was this stupid dinner', 'bang, noun: To have sex with someone. \x1D{} banged a right fit \x02bird\x02 last night!\x1D')

#@sopel.module.rule(r'^\.bang$')
@sopel.module.commands('bang')
def bang(bot, trigger):
    pass
    #bot.say(random.choice(mash).format(trigger.nick))

@sopel.module.rule(r'^\.badguys$')
def badguys(bot, trigger):
    bot.say('.killers')

@sopel.module.commands('gay')
def gay(bot, trigger):
    if trigger.group(2):
        bot.say('{} is gay'.format(trigger.group(2)))

@sopel.module.commands('banana')
def banana(bot, trigger):
    bot.say('I\'m a banana I\'m a banana I\'m a banana LOOK AT ME MOVE!')

@sopel.module.commands('breadcrumbs')
def breadcrumbs(bot, trigger):
    bot.say('Quack quack motherfucker')

@sopel.module.commands('naughtylist')
def naughtylist(bot, trigger):
    if trigger.group(3) and trigger.group(4):
        mode, name = trigger.group(2).split(' ', 1)
        if mode == 'add':
            bot.say('Added {} to naughty list'.format('greeny'))
    else:
        bot.say('Naughty list: greeny')

@sopel.module.rule(r'[Hh]ello there.*')
def kenobi(bot, trigger):
    bot.say('General Kenobi!')

@sopel.module.rule(r'^(?:\.)(np)(?:\s+((?:(\S+))?(?:\s+(\S+))?(?:\s+(\S+))?(?:\s+(\S+))?.*))?$')
def np(bot, trigger):
    user = trigger.nick
    if trigger.group(3):
        user = trigger.group(3)
    if 'Zenyatta' not in bot.users.keys():
        bot.say('%np {0}'.format(user))

@sopel.module.rule(r'.*\(y\)')
def boob(bot, trigger):
    bot.say('(.y.)')

@sopel.module.commands('nick')
def nick(bot, trigger):
    if not trigger.owner:
        bot.say('nah')
        return
    bot.write(('nick', trigger.group(2)))

@sopel.module.commands('gender')
def gender(bot, trigger):
    bot.say('Smasher')

@sopel.module.commands('bong')
def bong(bot, trigger):
    hour = datetime.now(tz=tz.gettz('Europe/London')).hour % 12
    if hour == 0:
        hour = 12
    bot.say("BONG " * hour)

@sopel.module.commands('bing')
def bing(bot, trigger):
    global mario
    if not mario:
        mario = True
        return

    mario = False
    bot.say('WAHOO')

@sopel.module.rule(r'hi ohboy')
def hi(bot, trigger):
    bot.say("hi {0}".format(trigger.nick))

@sopel.module.rule(r'send help')
def help(bot, trigger):
    bot.say("help")

@sopel.module.rule(r'hi$')
def hi(bot, trigger):
    bot.say("hi {0}".format(trigger.nick));
