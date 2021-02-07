# -*- coding: utf-8 -*-
import sopel.modules
import random
from time import time
from collections import defaultdict, namedtuple

helptext = namedtuple('HelpText', 'perms command line')

duck_tail = u'・゜゜・。。・゜゜'
duck = [u'\_o< ', u'\_O< ', u'\_0< ', u'\_\u00f6< ', u'\_\u00f8< ', u'\_\u00f3< ']
duck_noise = ['QUACK!', 'FLAP FLAP!', 'quack!']
chicken_noise = ['BOK!', 'SCRATCH SCRATCH!', 'bok!']
turkey_noise = ['GOBBLE!', 'HERP DERP!', 'gobble!']
o_noise = ['PAY BILLS', 'GHOSTING SYSOP', 'THE KEYS WILL BE SHARED !!!', '100 HOURSRS AND COUNTING !!!', 'NO ETA !!!', 'DEJA VU !!!', 'I\'M SO BUSY !!!', 'AIN\'T GOT NO TIME !!!']
duck_status = 0;
hosts = []
messages = 0
next_duck = time()
duck_time = time()
cooldown = defaultdict(int)

class DuckSection(sopel.config.types.StaticSection):
    channel = sopel.config.types.ValidatedAttribute('channel')
    enabled = sopel.config.types.ValidatedAttribute('enabled', bool, default=False)
    min_hosts = sopel.config.types.ValidatedAttribute('min_hosts', int, default=3)
    min_msg = sopel.config.types.ValidatedAttribute('min_msg', int, default=10)
    stat_count = sopel.config.types.ValidatedAttribute('stat_count', int, default=5)

def configure(config):
    config.define_section('duck', DuckSection)
    config.duck.configure_setting('channel', 'Channel to duck into')
    config.duck.configure_setting('enabled', 'Whether to duck')
    config.duck.configure_setting('min_hosts', 'Minimum unique hosts to duck')
    config.duck.configure_setting('min_msg', 'Minimum messages to duck')
    config.duck.configure_setting('stat_count', 'Number of users to print in stats')

def setup(bot):
    bot.config.define_section('duck', DuckSection)
    set_next()

    if not bot.memory.contains('help'):
        bot.memory['help'] = sopel.tools.SopelMemory()

    bot.memory['help']['duck'] = sopel.tools.SopelMemory()
    bot.memory['help']['duck']['short'] = "Duck hunting"
    bot.memory['help']['duck']['long'] = {
            helptext('admin', '!duck', 'Spawns a duck'),
            helptext('admin', '!chicken', 'Spawns a chicken'),
            helptext('all', '!bef', 'Befriends a duck'),
            helptext('all', '!befriend', 'Befriends a duck'),
            helptext('all', '!bang', 'Shoots a duck'),
            helptext('all', '!friends', 'Lists stats for good guys'),
            helptext('all', '!killers', 'Lists stats for bad guys'),
            helptext('all', '!badguys', 'Lists stats for bad guys'),
            helptext('all', '!ducks', 'Lists personal duck stats'),
            helptext('all', '!ducks <nick>', 'Lists someone elses personal duck stats'),
            helptext('all', '!duckstats', 'Lists channel duck stats')
            }

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

    global duck_status
    global duck_time

    if trigger.group(3):
        target = trigger.group(3)
    else:
        target = trigger.sender

    if target == bot.config.duck.channel:
        duck = generate_duck()[::-1]
    else:
        duck = generate_duck()

    bot.say(duck, target)

def generate_chicken():
    '''Try and randomize the chicken message so people can't highlight on it/script against it.'''
    rt = random.randint(1, len(duck_tail) - 1)
    dtail = duck_tail[:rt] + u' \u200b ' + duck_tail[rt:]
    dbody = random.choice(duck)
    rb = random.randint(1, len(dbody) - 1)
    dbody = dbody[:rb] + u'\u200b' + dbody[rb:]
    cnoise = random.choice(chicken_noise)
    rn = random.randint(1, len(cnoise) - 1)
    cnoise = cnoise[:rn] + u'\u200b' + cnoise[rn:]
    return u''.join((dtail, dbody, cnoise))

@sopel.module.commands('chicken')
def makechicken(bot, trigger):
    if not trigger.admin:
        bot.action('slaps {}'.format(trigger.nick))
        return

    global duck_status
    global duck_time

    if trigger.group(3):
        target = trigger.group(3)
    else:
        target = trigger.sender

    if target == bot.config.duck.channel:
        duck = generate_chicken()[::-1]
    else:
        duck = generate_chicken()

    bot.say(duck, target)

def generate_turkey():
    '''Try and randomize the turkey message so people can't highlight on it/script against it.'''
    rt = random.randint(1, len(duck_tail) - 1)
    dtail = duck_tail[:rt] + u' \u200b ' + duck_tail[rt:]
    dbody = random.choice(duck)
    rb = random.randint(1, len(dbody) - 1)
    dbody = dbody[:rb] + u'\u200b' + dbody[rb:]
    cnoise = random.choice(turkey_noise)
    rn = random.randint(1, len(cnoise) - 1)
    cnoise = cnoise[:rn] + u'\u200b' + cnoise[rn:]
    return u''.join((dtail, dbody, cnoise))

def generate_o():
    '''Try and randomize the O message so people can't highlight on it/script against it.'''
    rt = random.randint(1, len(duck_tail) - 1)
    dtail = duck_tail[:rt] + u' \u200b ' + duck_tail[rt:]
    dbody = random.choice(duck)
    rb = random.randint(1, len(dbody) - 1)
    dbody = dbody[:rb] + u'\u200b' + dbody[rb:]
    cnoise = random.choice(o_noise)
    rn = random.randint(1, len(cnoise) - 1)
    cnoise = cnoise[:rn] + u'\u200b' + cnoise[rn:]
    return u''.join((dtail, dbody, cnoise))

def make_bird(bot, real, breed):
    global duck_status

    if breed == 'duck':
        message = generate_duck()
        mode = 1
    elif breed == 'chicken':
        message = generate_chicken()
        mode = 2
    elif breed == 'turkey':
        message = generate_turkey()
        mode = 3
    elif breed == 'o':
        message = generate_o()
        mode = 4
    else:
        return

    bot.say(message, bot.config.duck.channel)

    if real:
        duck_status = mode

def set_next():
    global next_duck
    global messages
    global hosts
    next_duck = random.randint(int(time()) + 480, int(time()) + 3600)
    messages = 0
    hosts = []

@sopel.module.interval(11)
def do_duck(bot):
    global duck_status
    global duck_time
    if bot.config.duck.channel in bot.channels:
        if '#asdf' in bot.channels:
            bot.say("Status: {0}, Time: {1}, Messages: {2}, Hosts: {3}".format(duck_status,
                next_duck - time(), messages, len(hosts)), "#asdf");
        if (duck_status == 0 and next_duck <= time() and messages > bot.config.duck.min_msg and
            len(hosts) > bot.config.duck.min_hosts):
                duck_time = time()
                if random.randint(1, 100) > 10:
                    bot.say(generate_duck(), bot.config.duck.channel)
                    duck_status = 1
                elif random.randint(1, 100) > 40:
                    bot.say(generate_chicken(), bot.config.duck.channel)
                    duck_status = 2
                elif random.randint(1, 100) > 20:
                    bot.say(generate_turkey(), bot.config.duck.channel)
                    duck_status = 3
                else:
                    bot.say(generate_o(), bot.config.duck.channel)
                    duck_status = 4

@sopel.module.commands('bef', 'befriend', u'иуа')
def befriend(bot, trigger):
    if trigger.sender != bot.config.duck.channel:
        return

    attack(bot, trigger.nick, False)

@sopel.module.commands('bang', 'banfg', 'banmg', 'HAMBURGER', u'ифтп')
def bang(bot, trigger):
    if trigger.sender != bot.config.duck.channel:
        return

    attack(bot, trigger.nick, True)

def attack(bot, nick, bad):
    global duck_status
    global cooldown
    global messages
    if bad:
        miss = [
                "Duck slaps {0}.".format(nick), "Your gun jammed!",
                "Even if the duck was a barn door you still would've missed."
                ]
        no_duck = "There is no duck. What are you imzadi?"
        msg = "{0} you shot a duck in {1:.3f} seconds! You have killed {2} in {3}."
        chicken = "That's a chicken. This is a duck hunt."
        turkey = "That's a turkey. This is a fuck hunt."
        o = "That's a Duck-O, nice work {0}! You have killed {2} in {3}."
    else:
        miss = [
                "Who knew ducks could be so picky?",
                "The duck didn't want to be friends, maybe next time."
                ]
        no_duck = "You tried befriending a non-existent duck. That's fucking creepy."
        msg = "{0} you befriended a duck in {1:.3f} seconds! You have made friends with {2} in {3}."
        chicken = "That's a chicken."
        turkey = "That's turkey."
        o = "That's a Duck-O {0}, you don't want that. A duck leaves you in disgust. You have made friends with {2} in {3}."

    if duck_status == 0:
        bot.say(no_duck, bot.config.duck.channel)
        return

    if duck_status == 2:
        bot.say(chicken, bot.config.duck.channel)
        duck_status = 0
        set_next()
        return

    if duck_status == 3:
        bot.say(turkey, bot.config.duck.channel)
        duck_status = 0
        set_next()
        return

    shot = time()

    if nick in cooldown and cooldown[nick] > shot:
        cooldown[nick] = cooldown[nick] + 3
        bot.notice("You are in a cooldown period, you can try again in {0:.3f} seconds.".format(
            cooldown[nick] - shot), nick)
        return

    chance = hit_or_miss(duck_time, shot)
    
    if not random.random() <= chance and chance > 0.05:
        out = random.choice(miss) + " You can try again in 7 seconds."
        cooldown[nick] = shot + 7
        bot.say(out, bot.config.duck.channel)
        return

    if bad:
        score = bot.db.get_nick_value(nick, "killed") or 0
        diff = 2 if duck_status == 4 else 1
        bot.db.set_nick_value(nick, "killed", score + diff)
        bird = "duck"
    else:
        score = bot.db.get_nick_value(nick, "befriended") or 0
        diff = -1 if duck_status == 4 else 1
        bot.db.set_nick_value(nick, "befriended", score + diff)
        bird = "duck"

    if duck_status == 4:
        bot.say(o.format(nick, shot - duck_time, pluralise(bird, score + diff), bot.config.duck.channel))
    else:
        bot.say(msg.format(nick, shot - duck_time, pluralise(bird, score + diff), bot.config.duck.channel))
    set_next()

    duck_status = 0

@sopel.module.commands('friends', 'goodguys', 'duckerfrienders')
def friends(bot, trigger):
    if trigger.sender == bot.config.duck.channel:
        print_scores(bot, 'befriended', "Good Guys")

@sopel.module.commands('killers', 'badguys', 'duckerfuckers')
def killers(bot, trigger):
    if trigger.sender == bot.config.duck.channel:
        print_scores(bot, 'killed', "Bad Guys")

def print_scores(bot, score_type, message):
    scores = get_scores(bot, score_type)
    out = u"{0} in {1}: ".format(message, bot.config.duck.channel)
    out += u" • ".join([u"{0}: {1:,}".format(mangle(s[0]), s[1]) for s in scores])
    bot.say(out)

def get_scores(bot, score_type):
    scores = bot.db.execute(
            'SELECT MAX(n.canonical), MAX(v.value) '
            'FROM nick_values v '
            'JOIN nicknames n ON n.nick_id = v.nick_id '
            'WHERE v.key = ? '
            'GROUP BY v.nick_id '
            'ORDER BY v.value DESC ',
            [score_type]).fetchmany(bot.config.duck.stat_count)
    return scores

def mangle(nick):
    return u"{0}{1}{2}".format(nick[:1], unichr(int('200B', 16)), nick[1:])

@sopel.module.commands('ducks')
def ducks(bot, trigger):
    if trigger.sender != bot.config.duck.channel:
        return

    if trigger.group(3):
        nick = trigger.group(3)
    else:
        nick = trigger.nick

    killed = bot.db.get_nick_value(nick, 'killed') or 0
    befriended = bot.db.get_nick_value(nick, 'befriended') or 0

    if killed + befriended == 0:
        bot.say("It would regrettably appear that {0} has not participated in the duck hunt."
                .format(nick))
    else:
        bot.say(u"{0} has killed {1} and befriended {2} in {3}.".format(mangle(nick),
            pluralise("duck", killed), pluralise("duck", befriended), bot.config.duck.channel))

@sopel.module.commands('duckstats')
def duckstats(bot, trigger):
    if trigger.sender != bot.config.duck.channel:
        return

    killed = bot.db.execute(
            'SELECT SUM(value) '
            'FROM nick_values '
            'WHERE key = ? ',
            ['killed']).fetchone()[0] or 0

    befriended = bot.db.execute(
            'SELECT SUM(value) '
            'FROM nick_values '
            'WHERE key = ? ',
            ['befriended']).fetchone()[0] or 0

    if killed + befriended == 0:
        bot.say("It looks like there has been no duck activity.")
    else:
        bot.say("Duck Stats: {} killed and {} befriended in {}".format(
            killed, befriended, bot.config.duck.channel))

@sopel.module.commands('duckban')
def duckban(bot, trigger):
    if trigger.owner and trigger.group(3) and trigger.sender == bot.config.duck.channel:
        bot.say("{0} banned from duck hunt".format(trigger.group(3)))

@sopel.module.commands('duckforgive')
def duckforgive(bot, trigger):
    if trigger.owner and trigger.group(3) and trigger.sender == bot.config.duck.channel:
        bot.say("Not implemented")

def pluralise(word, count):
    if count == 1:
        return "{0} {1}".format(str(count), word)
    else:
        return "{0} {1}s".format(str(count), word)

def hit_or_miss(deploy, shot):
    if shot - deploy < 1:
        return 0.05
    elif 1 <= shot - deploy < 3:
        return random.uniform(0.4, 0.6)
    elif 3 <= shot - deploy <= 7:
        return random.uniform(0.6, 0.75)
    else:
        return 1

@sopel.module.rule('^[^!](.*)')
def tally(bot, trigger):
    if trigger.sender != bot.config.duck.channel:
        return
    global messages
    global hosts
    if not trigger.host in hosts:
        hosts.append(trigger.host)
    messages = messages + 1

def merge(bot, nick, alt):
    befo = bot.db.get_nick_value(nick, 'befriended') or 0
    befn = bot.db.get_nick_value(alt, 'befriended') or 0
    killo = bot.db.get_nick_value(nick, 'killed') or 0
    killn = bot.db.get_nick_value(alt, 'killed') or 0

    bot.db.set_nick_value(nick, 'befriended', befo + befn)
    bot.db.set_nick_value(nick, 'killed', killo + killn)
    return "{0} killed, {1} befriended".format(befn, killn)

