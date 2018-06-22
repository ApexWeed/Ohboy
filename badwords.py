import sopel.module
import collections

helptext = collections.namedtuple('HelpText', 'perms command line')

class BadwordsSection(sopel.config.types.StaticSection):
    badwords = sopel.config.types.ListAttribute('badwords')

def configure(config):
    config.define_section('badwords', BadwordsSection)
    config.admin.configure_setting('badwords', 'List of kickable words')

def setup(bot):
    bot.config.define_section('badwords', BadwordsSection)

    if not bot.memory.contains('help'):
        bot.memory['help'] = sopel.tools.SopelMemory()
    
    bot.memory['help']['badwords'] = sopel.tools.SopelMemory()
    bot.memory['help']['badwords']['short'] = 'Kicks people for saying bad words'
    bot.memory['help']['badwords']['long'] = {
            helptext('all', '!badwords', 'Lists bad words'),
            helptext('all', '!badwords list', 'Lists bad words'),
            helptext('admin', '!badwords add <word>', 'Adds a bad word to the list'),
            helptext('admin', '!badwords del <word>', 'Removes a bad word from the list')
            }

@sopel.module.rule('(.*)')
def badwords_trigger(bot, trigger):
    if len(bot.config.badwords.badwords) == 0:
        return

    if not trigger.admin and not trigger.is_privmsg:
        try:
            word = next(x for x in bot.config.badwords.badwords if x in trigger.group(1).lower())
            bot.write(('KICK', trigger.sender, trigger.nick), '{} is bampersand'.format(word))
        except:
            pass

@sopel.module.commands('badwords')
def badwords(bot, trigger):
    if not trigger.group(3) or trigger.group(3) == 'list':
        bot.say('Bad words: %s' % ', '.join(bot.config.badwords.badwords))
    elif trigger.group(3) == 'add' and trigger.group(4) and trigger.admin:
        wlist = bot.config.badwords.badwords
        wlist.append(trigger.group(2)[len(trigger.group(3)) + 1:])
        bot.config.badwords.badwords = wlist
        bot.say('Bad words: %s' % ', '.join(bot.config.badwords.badwords))
        bot.config.save()
    elif trigger.group(3) == 'del' and trigger.group(4) and trigger.admin:
        wlist = bot.config.badwords.badwords
        wlist.remove(trigger.group(2)[len(trigger.group(3)) + 1:])
        bot.config.badwords.badwords = list(filter(None, wlist))
        bot.say('Bad words: %s' % ', '.join(bot.config.badwords.badwords))
        bot.config.save()
