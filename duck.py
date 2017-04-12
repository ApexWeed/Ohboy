# -*- coding: utf-8 -*-
import sopel.modules
import random

duck_tail = u'・゜゜・。。・゜゜'
duck = [u'\_o< ', u'\_O< ', u'\_0< ', u'\_\u00f6< ', u'\_\u00f8< ', u'\_\u00f3< ']
duck_noise = ['QUACK!', 'FLAP FLAP!', 'quack!']

def generate_duck():
    '''Try and randomize the duck message so people can't highlight on it/script against it.'''
    rt = random.randint(1, len(duck_tail) - 1)
    dtail = duck_tail[:rt] + u' \u200b ' + duck_tail[rt:]
    dbody = random.choice(duck)
    rb = random.randint(1, len(dbody) - 1)
    dbody = dbody[:rb] + u'\u200b' + dbody[rb:]
    dnoise = random.choice(duck_noise)
    rn = random.randint(1, len(dnoise) - 1)
    dnoise = dnoise[:rn] + u'\u200b' + dnoise[rn:]
    return u''.join((dtail, dbody, dnoise))

@sopel.module.commands('duck')
def makeduck(bot, trigger):
    if not trigger.admin:
        bot.action('slaps {}'.format(trigger.nick))
        return

    if trigger.group(3):
        bot.say(generate_duck(), trigger.group(3))
    else:
        bot.say(generate_duck())
