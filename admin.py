# coding=utf-8
"""
admin.py - Sopel admin module that actually works
"""

import sopel.module
import collections
import sys

helptext = collections.namedtuple('HelpText', 'perms command line')

class AdminSection(sopel.config.types.StaticSection):
    hold_ground = sopel.config.types.ValidatedAttribute('hold_ground', bool, default=False)

def configure(config):
    config.define_section('admin', AdminSection)
    config.admin.configure_setting('hold_ground', 'Automatically re-join after being kicked?')

def setup(bot):
    bot.config.define_section('admin', AdminSection)

    if not bot.memory.contains('help'):
        bot.memory['help'] = sopel.tools.SopelMemory()
    
    bot.memory['help']['admin'] = sopel.tools.SopelMemory()
    bot.memory['help']['admin']['short'] = 'Admin tools'
    bot.memory['help']['admin']['long'] = {
            helptext('all', '!admin list', 'Lists admins'),
            helptext('admin', '!op <channel> [nick]', 'Makes you, or nick op'),
            helptext('admin', '!deop <channel> [nick]', 'Makes you, or nick not op'),
            helptext('admin', '!mode <channel> <mode> [nick]', 'Sets you, or nick to the specified mode'),
            helptext('admin', '!kick <channel> <nick> <reason>', 'Kicks a nick from the channel'),
            helptext('admin', '!ban <channel> <banmask>', 'Bans a hostmask from the channel'),
            helptext('admin', '!unban <channel> <banmask> <reason>', 'Unbans a hostmask from the channel'),
            helptext('admin', '!kickban <channel> <nick> <banmask>', 'Bans a hostmask and kicks a nick from the channel'),
            helptext('admin', '!topic <channel> <topic>', 'Sets the topic for a channel'),
            helptext('admin', '!me <channel> <action>', 'Makes the bot perform an action in a channel'),
            helptext('admin', '!msg <channel> <message>', 'Makes the bot say a message in a channel'),
            helptext('admin', '!join <channel>', 'Makes the bot join a channel'),
            helptext('admin', '!part <channel>', 'Makes the bot part a channel'),
            helptext('owner', '!quit [reason]', 'Makes the bot shutdown'),
            helptext('owner', '!save', 'Saves bot config'),
            helptext('owner', '!admin add <nick>', 'Adds a nick as an admin'),
            helptext('owner', '!admin del <nick>', 'Removes a nick from admin'),
            helptext('owner', '!pyver', 'Prints python version')
            }

@sopel.module.event('KICK')
@sopel.module.rule(r'.*')
def hold_ground(bot, trigger):
    if bot.config.admin.hold_ground:
        if trigger.args[1] == bot.nick:
            bot.join(trigger.sender)

@sopel.module.commands('op')
def op(bot, trigger):
    if not trigger.admin or not trigger.is_privmsg:
        return

    if trigger.group(3):
        if trigger.group(4):
            bot.write(('MODE', trigger.group(3), '+o', trigger.group(4)))
        else:
            bot.write(('MODE', trigger.group(3), '+o', trigger.nick))
    else:
        bot.reply('Specify a channel')

@sopel.module.commands('deop')
def deop(bot, trigger):
    if not trigger.admin or not trigger.is_privmsg:
        return

    if trigger.group(3):
        if trigger.group(4):
            bot.write(('MODE', trigger.group(3), '-o', trigger.group(4)))
        else:
            bot.write(('MODE', trigger.group(3), '-o', trigger.nick))
    else:
        bot.reply('Specify a channel')

@sopel.module.commands('mode')
def mode(bot, trigger):
    if not trigger.admin or not trigger.is_privmsg:
        return

    if trigger.group(3):
        if trigger.group(4):
            if trigger.group(5):
                bot.write(('MODE', trigger.group(3), trigger.group(4), trigger.group(5)))
            else:
                bot.write(('MODE', trigger.group(3), trigger.group(4), trigger.nick))
        else:
            bot.reply('Specify a mode')
    else:
        bot.reply('Specify a channel')

@sopel.module.commands('kick')
def kick(bot, trigger):
    if not trigger.admin or not trigger.is_privmsg:
        return

    if trigger.group(3):
        if trigger.group(4):
            if trigger.group(5):
                channel, nick, reason = trigger.group(2).split(' ', 2)
                bot.write(('KICK', channel, nick), reason)
            else:
                bot.reply('Specify a reason')
        else:
            bot.reply('Specify a nick')
    else:
        bot.reply('Specify a channel')

@sopel.module.commands('ban')
def ban(bot, trigger):
    if not trigger.admin or not trigger.is_privmsg:
        return

    if trigger.group(3):
        if trigger.group(4):
            bot.write(('MODE', channel, '+b', banmask))
        else:
            bot.reply('Specify a banmask')
    else:
        bot.reply('Specify a channel')

@sopel.module.commands('unban')
def unban(bot, trigger):
    if not trigger.admin or not trigger.is_privmsg:
        return
    if trigger.group(3):
        if trigger.group(4):
            bot.write(('MODE', trigger.group(3), '-b', trigger.group(4)))
        else:
            bot.reply('Specify a banmask')
    else:
        bot.reply('Specify a channel')

@sopel.module.commands('kickban')
def kickban(bot, trigger):
    if not trigger.admin or not trigger.is_privmsg:
        return

    if trigger.group(3):
        if trigger.group(4):
            if trigger.group(5):
                if trigger.group(6):
                    channel, nick, banmask, reason = trigger.group(2).split(' ', 3)
                bot.write(('MODE', channel, '+b', banmask))
                bot.write(('KICK', channel, nick), reason)
            else:
                bot.reply('Specify a banmask')
        else:
            bot.reply('Specify a nick')
    else:
        bot.reply('Specify a channel')

@sopel.module.commands('topic')
def topic(bot, trigger):
    if not trigger.admin or not trigger.is_privmsg:
        return

    if trigger.group(3):
        if trigger.group(4):
            bot.write(('TOPIC', trigger.group(3)), trigger.group(2)[len(trigger.group(3)) + 1:])
        else:
            bot.reply('Specify the topic')
    else:
        bot.reply('Specify the channel')

@sopel.module.commands('me')
def me(bot, trigger):
    if not trigger.admin or not trigger.is_privmsg:
        return
    
    if trigger.group(3):
        if trigger.group(4):
            bot.msg(trigger.group(3), '\x01ACTION %s\x01' % trigger.group(2)[len(trigger.group(3)) + 1:])
        else:
            bot.reply('Specify an action')
    else:
        bot.reply('Specify a target')

@sopel.module.commands('msg')
def msg(bot, trigger):
    if not trigger.admin or not trigger.is_privmsg:
        return

    if trigger.group(3):
        if trigger.group(4):
            bot.msg(trigger.group(3), trigger.group(2)[len(trigger.group(3)) + 1:])
        else:
            bot.reply('Specify a message')
    else:
        bot.reply('Specify a target')

@sopel.module.commands('join')
def join(bot, trigger):
    if not trigger.admin or not trigger.is_privmsg:
        return

    if trigger.group(3):
        if trigger.group(4):
            bot.join(trigger.group(3), trigger.group(4))
        else:
            bot.join(trigger.group(3))
    else:
        bot.reply('Specify a channel')

@sopel.module.commands('part')
def part(bot, trigger):
    if not trigger.admin or not trigger.is_privmsg:
        return

    if trigger.group(3):
        if trigger.group(4):
            bot.part(trigger.group(3), trigger.group(2)[len(trigger.group(3)) + 1:])
        else:
            bot.part(trigger.group(3))
    else:
        bot.reply('Specify a channel')

@sopel.module.commands('quit')
def quit(bot, trigger):
    if not trigger.owner or not trigger.is_privmsg:
        return
    
    bot.quit(trigger.group(2) or '%s informs me I am to die' % trigger.nick)

@sopel.module.commands('save')
def save(bot, trigger):
    if not trigger.owner or not trigger.is_privmsg:
        return

    bot.config.save()

@sopel.module.commands('pyver')
def pyver(bot, trigger):
    if not trigger.owner or not trigger.is_privmsg:
        return

    bot.reply('Python %s' % sys.version)

@sopel.module.commands('admin')
def admin(bot, trigger):
    if trigger.group(3) == 'list':
        bot.say('Admins: %s' % ', '.join(bot.config.core.admins))
        return

    if not trigger.is_privmsg and not trigger.admin:
        return

    if trigger.group(3) == 'add':
        if trigger.group(4):
            alist = bot.config.core.admins
            alist.append(trigger.group(4))
            bot.config.core.admins = alist
            bot.config.save()
            bot.say('You are now a bot admin', trigger.group(4))
            bot.reply('%s added to admins' % trigger.group(4))
    elif trigger.group(3) == 'del':
        if trigger.group(4):
            alist = bot.config.core.admins
            alist.remove(trigger.group(4))
            bot.config.core.admins = alist
            bot.config.save()
            bot.say('You are no longer a bot admin', trigger.group(4))
            bot.reply('%s removed from admins' % trigger.group(4))


