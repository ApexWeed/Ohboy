# coding=utf-8
"""
admin.py - Sopel admin module that actually works
"""

import sopel.module

class AdminSection(sopel.config.types.StaticSection):
    hold_ground = sopel.config.types.ValidatedAttribute('hold_ground', bool, default=False)

def configure(config):
    config.define_section('admin', AdminSection)
    config.admin.configure_setting('hold_ground', 'Automatically re-join after being kicked?')

def setup(bot):
    bot.config.define_section('admin', AdminSection)

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
def deop(bot, trigger):
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
            bot.write(('KICK', trigger.group(3), trigger.group(4)))
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
            bot.write(('MODE', trigger.group(3), '+b', trigger.group(4)))
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
                bot.write(('MODE', trigger.group(3), '+b', trigger.group(5)))
                bot.write(('KICK', trigger.group(3), trigger.group(4)))
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

@sopel.module.commands('admin')
def admin(bot, trigger):
    if not trigger.owner or not trigger.is_privmsg:
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


