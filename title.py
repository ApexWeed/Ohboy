from __future__ import unicode_literals, absolute_import, print_function, division

import re
import sopel.module
import collections
import requests
from sopel import web, tools, __version__

helptext = collections.namedtuple('HelpText', 'perms command line')

USER_AGENT = 'Sopel/{} (http://sopel.chat)'.format(__version__)
default_headers = {'User-Agent': USER_AGENT}

url_finder = None
# These are used to clean up the title tag before actually parsing it. Not the
# world's best way to do this, but it'll do for now.
title_tag_data = re.compile('<(/?)title( [^>]+)?>', re.IGNORECASE)
quoted_title = re.compile('[\'"]<title>[\'"]', re.IGNORECASE)

# This is another regex that presumably does something important.
re_dcc = re.compile(r'(?i)dcc\ssend')

# This sets the maximum number of bytes that should be read in order to find
# the title. We don't want it too high, or a link to a big file/stream will
# just keep downloading until there's no more memory. 640k ought to be enough
# for anybody.
max_bytes = 655360

def setup(bot):
    global url_finder
    url_finder = re.compile(r'(?u)((?:http|https|ftp)(?:://\S+))', re.IGNORECASE)

    if not bot.memory.contains('last_seen_url'):
        bot.memory['last_seen_url'] = tools.SopelMemory()
    if not bot.memory.contains('url_callbacks'):
        bot.memory['url_callbacks'] = tools.SopelMemory()
    if not bot.memory.contains('help'):
        bot.memory['help'] = tools.SopelMemory()

    bot.memory['help']['title'] = tools.SopelMemory()
    bot.memory['help']['title']['short'] = 'Privmsg or notices link titles'
    bot.memory['help']['title']['long'] = {
            helptext('all', '!title [status]', 'Prints status of titles for you'),
            helptext('all', '!title on|notice', 'Sets titles to notice'),
            helptext('all', '!title privmsg', 'Sets titles to privmsg'),
            helptext('all', '!title off', 'Turns titles off')
            }

@sopel.module.commands('title')
def title(bot, trigger):
    if not trigger.group(2) or trigger.group(3) == 'status':
        status = bot.db.get_nick_value(trigger.nick, 'title')
        bot.notice('Your titles are set to {}'.format(status or 'off'), trigger.nick)

    if trigger.group(3) == 'on':
        bot.db.set_nick_value(trigger.nick, 'title', 'on')
        bot.notice('Titles enabled', trigger.nick)
    elif trigger.group(3) == 'privmsg':
        bot.db.set_nick_value(trigger.nick, 'title', 'privmsg')
        bot.notice('Titles enabled (privmsg)', trigger.nick)
    elif trigger.group(3) == 'notice':
        bot.db.set_nick_value(trigger.nick, 'title', 'notice')
        bot.notice('Titles enabled (notice)', trigger.nick)
    elif trigger.group(3) == 'off':
        bot.db.set_nick_value(trigger.nick, 'title', 'off')
        bot.notice('Titles disabled', trigger.nick)

@sopel.module.rule('(?u).*(https?://\S+).*')
def title_auto(bot, trigger):
    # Avoid fetching known malicious links
    if 'safety_cache' in bot.memory and trigger in bot.memory['safety_cache']:
        if bot.memory['safety_cache'][trigger]['positives'] > 1:
            return

    urls = re.findall(url_finder, trigger)
    if len(urls) == 0:
        return

    results = process_urls(bot, trigger, urls)
    bot.memory['last_seen_url'][trigger.sender] = urls[-1]

    for title, domain in results[:4]:
        message = '[ {} ] - {}'.format(title, domain)
        # Guard against responding to other instances of this bot.
        if message != trigger:
            if trigger.sender in bot.channels:
                for user in bot.channels[trigger.sender].users:
                    enabled = bot.db.get_nick_value(user, 'title') or 'off'
                    if enabled == 'on' or enabled == 'notice':
                        bot.notice(message, user)
                    elif enabled == 'privmsg':
                        bot.say(message, user)

def process_urls(bot, trigger, urls):
    results = []
    for url in urls:
        try:
            url = web.iri_to_uri(url)
        except:
            pass

        title = None

        for regex, function in tools.iteritems(bot.memory['url_callbacks']):
            match = regex.search(url)
            if match is not None:
                title = function(bot, trigger, match)
                if title:
                    results.append((title, get_hostname(url)))
                    break

        if not title:
            title = find_title(url, verify=bot.config.core.verify_ssl)
            if title:
                results.append((title, get_hostname(url)))
    return results

def find_title(url, verify=True):
    """Return the title for the given URL."""
    try:
        response = requests.get(url, stream=True, verify=verify, headers=default_headers)
    except:
        return None
    
    try:
        content = b''
        for byte in response.iter_content(chunk_size=512):
            content += byte
            if b'</title>' in content or len(content) > max_bytes:
                break
        content = content.decode('utf-8', errors='ignore')
    finally:
        # need to close the connexion because we have not read all the data
        response.close()

    # Some cleanup that I don't really grok, but was in the original, so
    # we'll keep it (with the compiled regexes made global) for now.
    content = title_tag_data.sub(r'<\1title>', content)
    content = quoted_title.sub('', content)

    start = content.find('<title>')
    end = content.find('</title>')
    if start == -1 or end == -1:
        return
    title = web.decode(content[start + 7:end])
    title = title.strip()[:200]

    title = ' '.join(title.split())  # cleanly remove multiple spaces

    # More cryptic regex substitutions. This one looks to be myano's invention.
    title = re_dcc.sub('', title)

    return title or None

def get_hostname(url):
    idx = 7
    if url.startswith('https://'):
        idx = 8
    elif url.startswith('ftp://'):
        idx = 6
    hostname = url[idx:]
    slash = hostname.find('/')
    if slash != -1:
        hostname = hostname[:slash]
    return hostname
