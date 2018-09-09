# coding=utf-8
from __future__ import unicode_literals, absolute_import, print_function, division

import collections
import sys
import time
from sopel.tools import iteritems
import sopel.loader
import sopel.module
import subprocess

helptext = collections.namedtuple('HelpText', 'perms command line')

def setup(bot):
    if not bot.memory.contains('help'):
        bot.memory['help'] = sopel.tools.SopelMemory()

    bot.memory['help']['reload'] = sopel.tools.SopelMemory()
    bot.memory['help']['reload']['short'] = 'Reloads modules at runtime'
    bot.memory['help']['reload']['long'] = {
            helptext('owner', '!reload [module]', 'Reloads either specified module or all'),
            helptext('owner', '!reload-config', 'Reloads the whole Sopel config, and reloads modules'),
            helptext('owner', '!load <module>', 'Loads a module')
            }

@sopel.module.commands('reload-config')
@sopel.module.priority('low')
@sopel.module.thread(False)
def conf_reload(bot, trigger):
    """Reloads configs"""
    if not trigger.owner:
        return
    bot.config.__init__(bot.config.filename)
    bot.notice('Configs reloaded', trigger.nick)
    reload(bot, trigger)

@sopel.module.commands("reload")
@sopel.module.priority("low")
@sopel.module.thread(False)
def reload(bot, trigger):
    """Reloads a module, for use by admins only."""
    if not trigger.admin or not trigger.is_privmsg:
        return

    name = trigger.group(2)

    if not name or name == '*' or name.upper() == 'ALL THE THINGS':
        for module in bot.config.core.enable:
            try:
                module = sys.modules[module]
                if hasattr(module, 'unload'):
                    module.unload(bot)
            except:
                pass
                
        bot._callables = {
            'high': collections.defaultdict(list),
            'medium': collections.defaultdict(list),
            'low': collections.defaultdict(list)
        }
        bot._command_groups = collections.defaultdict(list)

        bot.setup()
        return bot.notice('Modules reloaded', trigger.nick)

    if name not in sys.modules:
        return bot.reply('{}: not loaded, try the `load` command'.format(name), trigger.nick)

    old_module = sys.modules[name]
    if hasattr(old_module, 'unload'):
        old_module.unload(bot)

    old_callables = {}
    for obj_name, obj in iteritems(vars(old_module)):
        bot.unregister(obj)

    # Also remove all references to sopel callables from top level of the
    # module, so that they will not get loaded again if reloading the
    # module does not override them.
    for obj_name in old_callables.keys():
        delattr(old_module, obj_name)

    # Also delete the setup function
    if hasattr(old_module, "setup"):
        delattr(old_module, "setup")

    modules = sopel.loader.enumerate_modules(bot.config)
    path, type_ = modules[name]
    load_module(bot, name, path, type_, trigger.nick)


def load_module(bot, name, path, type_, nick):
    module, mtime = sopel.loader.load_module(name, path, type_)
    relevant_parts = sopel.loader.clean_module(module, bot.config)

    bot.register(*relevant_parts)

    # TODO sys.modules[name] = module
    if hasattr(module, 'setup'):
        module.setup(bot)

    modified = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(mtime))

    bot.notice('{} (version: {})'.format(module, modified), nick)

@sopel.module.commands("load")
@sopel.module.priority("low")
@sopel.module.thread(False)
def load(bot, trigger):
    """Loads a module, for use by admins only."""
    if not trigger.admin or not trigger.is_privmsg:
        return

    name = trigger.group(2)
    path = ''
    if not name:
        return bot.notice('Load what?', trigger.nick)

    if name in sys.modules:
        return bot.notice('Module already loaded, use reload', trigger.nick)

    mods = sopel.loader.enumerate_modules(bot.config)
    if name not in mods:
        return bot.notice('Module {} not found'.format(name), trigger.nick)
    path, type_ = mods[name]
    load_module(bot, name, path, type_, trigger.nick)
