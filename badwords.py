import sopel.module

class BadwordsSection(sopel.config.types.StaticSection):
    badwords = sopel.config.types.ListAttribute('badwords')

def configure(config):
    config.define_section('badwords', BadwordsSection)
    config.admin.configure_setting('badwords', 'List of kickable words')

def setup(bot):
    bot.config.define_section('badwords', BadwordsSection)

@sopel.module.rule('(.*)')
def badwords_trigger(bot, trigger):
    if not trigger.admin and not trigger.is_privmsg:
        if any(word in trigger.group(1) for word in bot.config.badwords.badwords):
            bot.write(('KICK', trigger.sender, trigger.nick))

@sopel.module.commands('badwords')
def badwords(bot, trigger):
    if not trigger.group(3) or trigger.group(3) == 'list':
        bot.say('Bad words: %s' % ', '.join(bot.config.badwords.badwords))
    elif trigger.group(3) == 'add' and trigger.admin:
        wlist = bot.config.badwords.badwords
        wlist.append(trigger.group(2)[len(trigger.group(3)) + 1:])
        bot.config.badwords.badwords = wlist
        bot.say('Bad words: %s' % ', '.join(bot.config.badwords.badwords))
        bot.config.save()
    elif trigger.group(3) == 'del' and trigger.admin:
        wlist = bot.config.badwords.badwords
        wlist.remove(trigger.group(2)[len(trigger.group(3)) + 1:])
        bot.config.badwords.badwords = wlist
        bot.say('Bad words: %s' % ', '.join(bot.config.badwords.badwords))
        bot.config.save()
