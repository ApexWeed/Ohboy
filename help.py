import sopel.module
import collections
import os
import cgi

helptext = collections.namedtuple('HelpText', 'perms command line')

class HelpSection(sopel.config.types.StaticSection):
    gen_html = sopel.config.types.ValidatedAttribute('gen_html', bool, default=False)
    html_file = sopel.config.types.FilenameAttribute('html_file', relative=False)

def configure(config):
    config.define_section('help', HelpSection)
    config.help.configure_setting('gen_html', 'Enable HTML help generation?')
    config.help.configure_setting('html_file', 'Filename to output HTML help to')

def setup(bot):
    bot.config.define_section('help', HelpSection)

    if not bot.memory.contains('help'):
        bot.memory['help'] = sopel.tools.SopelMemory()

    bot.memory['help']['help'] = sopel.tools.SopelMemory()
    bot.memory['help']['help']['short'] = 'Provides help'
    bot.memory['help']['help']['long'] = {
            helptext('all', '!help', 'Displays help'),
            helptext('all', '!help <module>', 'Displays module help'),
            helptext('admin', '!help genhtml', 'Generates a new HTML help page')
            }

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
        bot.say('Use !help <module> for module help')
        for key, value in bot.memory['help'].items():
            say_direct(bot, trigger.nick, '%s: %s' % (key, value['short']))
    elif module == 'genhtml':
        if not trigger.admin or not bot.config.help.gen_html or not os.path.isfile(bot.config.help.html_file):
            return

        fs = open(bot.config.help.html_file, 'w')
        fs.write('<html><head><title>{} command reference</title></head><body>'.format(bot.nick))

        for module, help in bot.memory['help'].items():
            fs.write('<h2>{}</h2><p>{}</p>'.format(module, cgi.escape(help['short'])))
            if 'long' in help:
                fs.write('<ul>')
                for cmd in help['long']:
                    fs.write('<li class="{}"><tt>{}</tt>: {}</li>'.format(cmd.perms, cgi.escape(cmd.command), cgi.escape(cmd.line)))
                fs.write('</ul>')

        fs.write('</body></html>')
        bot.reply('Generated!')
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

