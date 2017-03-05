import sopel.module

@sopel.module.commands('op')
@sopel.module.require_privmsg('This command only works as a private message.')
@sopel.module.require_admin('This command requires admin provileges.')
def op(bot, trigger):
    if trigger.group(3):
        if trigger.group(4):
            bot.write(('MODE', trigger.group(3), '+o', trigger.group(4)))
        else:
            bot.write(('MODE', trigger.group(3), '+o', trigger.nick))
    else:
        bot.reply('Specify a channel')

@sopel.module.commands('deop')
@sopel.module.require_privmsg('This command only works as a private message.')
@sopel.module.require_admin('This command requires admin provileges.')
def deop(bot, trigger):
    if trigger.group(3):
        if trigger.group(4):
            bot.write(('MODE', trigger.group(3), '-o', trigger.group(4)))
        else:
            bot.write(('MODE', trigger.group(3), '-o', trigger.nick))
    else:
        bot.reply('Specify a channel')
