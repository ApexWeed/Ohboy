import sopel.module
import collections

helptext = collections.namedtuple('HelpText', 'perms command line')

def setup(bot):
    if not bot.memory.contains('help'):
        bot.memory['help'] = sopel.tools.SopelMemory()

def say_direct(bot, target, message):
    args = ('PRIVMSG', target)
    bot.write(args, message[:400])
    if len(message) > 400:
        say_direct(bot, target, message)

@sopel.module.commands('help')
def help(bot, trigger):
    if not trigger.is_privmsg:
        return

    module = trigger.group(3)
    if not module or module == 'all':
        for key, value in bot.memory['help'].items():
            say_direct(bot, trigger.nick, '%s: %s' % (key, value['short']))
    elif module in bot.memory['help']:
        if 'long' in bot.memory['help'][module]:
            count = 0
            for cmd in bot.memory['help'][module]['long']:
                if cmd.perms == 'all' or (cmd.perms == 'admin' and trigger.admin) or (cmd.perms == 'owner' and trigger.owner) or (cmd.perms == 'user' and not trigger.admin):
                    say_direct(bot, trigger.nick, '%s: %s' % (cmd.command, cmd.line))
                    count = count + 1
            if count == 0:
                bot.say('No extended help available for %s' % module)
        else:
            bot.say('No extended help available for %s' % module)
