import sopel.module
import collections
import whatapi
import HTMLParser
import urlparse
import re
import cPickle as pickle
import os
from subprocess import call

helptext = collections.namedtuple('HelpText', 'perms command line')

api = None
parser = HTMLParser.HTMLParser()
regex = re.compile(r"https://apollo\.rip/(.*?)\.php\??(.*)")

class ApolloSection(sopel.config.types.StaticSection):
    username = sopel.config.types.ValidatedAttribute('username')
    password = sopel.config.types.ValidatedAttribute('password')
    server = sopel.config.types.ValidatedAttribute('server')
    cookie_file = sopel.config.types.FilenameAttribute('cookie_file', relative=False)
    simulate = sopel.config.types.ValidatedAttribute('simulate', bool, default=False)
    apollo_config = sopel.config.types.FilenameAttribute('apollo_config', relative=True)

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return '{:3.1f}{}{}'.format(num, unit, suffix)
        num /= 1024.0
    return '{:.1f}{}{}'.format(num, 'Yi', suffix)

def configure(config):
    config.define_section('apollo', ApolloSection)
    config.apollo.configure_setting('username', 'Username for Apollo integration')
    config.apollo.configure_setting('password', 'Password for Apollo integration')
    config.apollo.configure_setting('server', 'Server for Apollo integration')
    config.apollo.configure_setting('cookie_file', 'File to store Apollo session data')
    config.apollo.configure_setting('simulate', 'Whether to allow simulation')
    config.apollo.configure_setting('apollo_config', 'Path to config for apollo simulator')

def setup(bot):
    global api
    bot.config.define_section('apollo', ApolloSection)

    if not api:
        if os.path.isfile(bot.config.apollo.cookie_file):
            try:
                cookies = pickle.load(open(bot.config.apollo.cookie_file, 'rb'))
                api = whatapi.WhatAPI(username=bot.config.apollo.username, password=bot.config.apollo.password, server=bot.config.apollo.server, cookies=cookies)
            except:
                api = whatapi.WhatAPI(username=bot.config.apollo.username, password=bot.config.apollo.password, server=bot.config.apollo.server)

        else:
            api = whatapi.WhatAPI(username=bot.config.apollo.username, password=bot.config.apollo.password, server=bot.config.apollo.server)

    if not bot.memory.contains('help'):
        bot.memory['help'] = sopel.tools.SopelMemory()

    bot.memory['help']['apollo'] = sopel.tools.SopelMemory()
    bot.memory['help']['apollo']['short'] = 'Feature parity with APOLLO'
    bot.memory['help']['apollo']['long'] = {
            helptext('all', '!sandwich', 'Requests a sandwich'),
            helptext('all', '!sudosandwich', 'Requests a sandwich'),
            helptext('all', '!slap <target>', 'Slaps somebody around'),
            helptext('all', '!apollo stats', 'Prints site stats'),
            helptext('all', '!apollo user <id>', 'Prints user info'),
            helptext('all', '!apollo user <name>', 'Prints user search results'),
            helptext('all', '!apollo loadavg', 'Prints loadavg for some reason'),
            helptext('all', '!apollo top10 torrents day|week|overall|snatched|data|seeded', 'Searches torrent top 10'),
            helptext('all', '!apollo top10 tags ut|ur|v', 'Searches tag top 10'),
            helptext('all', '!apollo top10 users ul|dl|numul|uls|dls', 'Searches user top 10'),
            helptext('admin', '!sudoslap <count> <target>', 'Slaps somebody around. A bunch'),
            helptext('admin', '!simulate', 'Engage in an authentic replication of the day to day life of an APOLLO')
            }
    
    if not bot.memory.contains('url_callbacks'):
        bot.memory['url_callbacks'] = sopel.tools.SopelMemory()
    bot.memory['url_callbacks'][regex] = title

def unload(bot):
    if not save(bot):
        bot.say('Could not save apollo session to {}'.format(bot.config.apollo.cookie_file))

def shutdown(bot):
    save(bot)

def save(bot):
    try:
        pickle.dump(api.session.cookies, open(bot.config.apollo.cookie_file, 'wb'))
    except:
        return False
    return True

@sopel.module.commands('slap')
def slap(bot, trigger):
    if trigger.group(2):
        bot.say(trigger.nick + ' slaps ' + trigger.group(2))

@sopel.module.commands('sandwich')
def sandwich(bot, trigger):
    bot.say('Make it yourself, ' + trigger.nick)

@sopel.module.commands('sudosandwich')
def sudosandwich(bot, trigger):
    bot.say('Here you go, ' + trigger.nick + ' [sandwich]')

@sopel.module.commands('sudoslap')
def sudoslap(bot, trigger):
    if not trigger.admin or not trigger.group(3) or not trigger.group(4):
        return

    try:
        count = int(trigger.group(3))
    except:
        return

    for i in range(0, count):
        bot.say(trigger.nick + ' slaps ' + trigger.group(2)[len(trigger.group(3)) + 1:] + ', take ' + str(i + 1))

@sopel.module.commands('simulate')
def simulate(bot, trigger):
    if not trigger.admin:
        return

    if bot.config.apollo.simulate:
        if bot.config.core.host == 'irc.scratch-network.net':
            bot.say('#resonance :You need to be identified to a registered account to join this channel')
        else:
            call(['sopel', '-c', bot.config.apollo.apollo_config])

@sopel.module.commands('apollo')
def apollo(bot, trigger):
    if not api:
        return

    command = trigger.group(3)
    args = trigger.group(2)[len(trigger.group(3)):]

    if command == 'user':
        if trigger.group(4).isdigit():
            bot.say(user(trigger.group(4)))
        else:
            json = api.request('usersearch', search=args)
            if len(json['response']['results']) == 1:
                bot.say(user(json['response']['results'][0]['userId']))
                return

            res = u'Results: {}'.format(', '.join([u'{} ({})'.format(s_user['username'], s_user['userId']) for s_user in json['response']['results']]))
            bot.say(res)
    elif command == 'stats':
        json = api.request('stats')
        bot.say(u'Users: {}/{} ({} D / {} W / {} M) Torrents: {} Releases: {} Artists: {} Perfects: {} Reqs: {}/{} S/L: {}/{})'.format(
            json['response']['enabledUsers'],
            json['response']['maxUsers'],
            json['response']['usersActiveThisDay'],
            json['response']['usersActiveThisWeek'],
            json['response']['usersActiveThisMonth'],
            json['response']['torrentCount'],
            json['response']['releaseCount'],
            json['response']['artistCount'],
            json['response']['perfectFlacCount'],
            json['response']['filledRequestCount'],
            json['response']['requestCount'],
            json['response']['seederCount'],
            json['response']['leecherCount']
            ))
    elif command == 'loadavg':
        json = api.request('loadavg')
        bot.say('Load average: {}'.format(json['response']['loadAverage']))
    elif command == 'top10':
        if trigger.group(4) == 'torrents':
            if trigger.group(5) in ('day', 'week', 'overall', 'snatched', 'data', 'seeded'):
                json = next((x for x in api.request('top10', type=trigger.group(4))['response'] if x['tag'] == trigger.group(5)), None)
                bot.say(u'{} ({} results)'.format(json['caption'], len(json['results'])))
                for torrent in json['results']:
                    bot.say(u'{} - {} ({}) [{} ({})] {}/torrents.php?id={}&torrentId={} [{}]'.format(
                        parser.unescape(torrent['artist']),
                        parser.unescape(torrent['groupName']),
                        torrent['groupYear'],
                        torrent['format'],
                        torrent['encoding'],
                        bot.config.apollo.server,
                        torrent['groupId'],
                        torrent['torrentId'],
                        ', '.join(torrent['tags'])
                        ), trigger.nick)
        elif trigger.group(4) == 'tags':
            if trigger.group(5) in ('ut', 'ur', 'v'):
                json = next((x for x in api.request('top10', type=trigger.group(4))['response'] if x['tag'] == trigger.group(5)), None)
                bot.say(u'{}: {})'.format(json['caption'], ', '.join(json['results'])))
        elif trigger.group(4) == 'users':
            if trigger.group(5) in ('ul', 'dl', 'numul', 'uls', 'dls'):
                json = next((x for x in api.request('top10', type=trigger.group(4))['response'] if x['tag'] == trigger.group(5)), None)
                bot.say(u'{} ({} results)'.format(json['caption'], len(json['results'])))
                for s_user in json['results']:
                    bot.say(u'{} ({}) Torrents: {} Up: {} ({}/s) Down: {} ({}/s) Joined: {}'.format(
                        s_user['username'],
                        s_user['id'],
                        s_user['numUploads'],
                        sizeof_fmt(s_user['uploaded']),
                        sizeof_fmt(s_user['upSpeed']),
                        sizeof_fmt(s_user['downloaded']),
                        sizeof_fmt(s_user['downSpeed']),
                        user['joinDate']
                        ))

def title(bot, trigger, match):
    if not api:
        return

    args = urlparse.parse_qs(urlparse.urlparse(match.group(0)).query)
    if match.group(1) == 'index':
        return 'Apollo - Main Page'
    elif match.group(1) == 'user':
        if 'id' in args:
            return user(args['id'])
        else:
            return 'Apollo - User Page'
    elif match.group(1) == 'torrents':
        if 'torrentid' in args:
            return torrent(args['torrentid'])
        elif 'id' in args:
            return group(args['id'])
        else:
            return 'Apollo - Torrents'
    elif match.group(1) == 'artist':
        if 'id' in args:
            return artist(args['id'])
        else:
            return 'Apollo - Artist'
    elif match.group(1) == 'forums':
        if 'threadid' in args:
            return thread(args['threadid'])
        else:
            return 'Apollo - Forums'
    elif match.group(1) == 'requests':
        if 'id' in args:
            return request(args['id'])
        else:
            return 'Apollo - Requests'
    else:
        return 'Apollo'

def user(id):
    json = api.request('user', id=id)
    return u'{} ({}): {} U {} D ({}) joined {}'.format(
            json['response']['username'],
            json['response']['personal']['class'],
            sizeof_fmt(json['response']['stats']['uploaded'] or 0),
            sizeof_fmt(json['response']['stats']['downloaded'] or 0),
            json['response']['stats']['ratio'], json['response']['stats']['joinedDate']
            )

def torrent(id):
    json = api.request('torrent', id=id)['response']
    return u'{} - {} ({}) [{} - {} ({})] [{}] Seeds: {} Leeches: {} Snatches: {}'.format(
            get_artists(json['group']['musicInfo']),
            parser.unescape(json['group']['name']),
            json['group']['year'],
            json['torrent']['media'],
            json['torrent']['format'],
            encoding(json['torrent']),
            ', '.join(json['group']['tags']),
            json['torrent']['seeders'],
            json['torrent']['leechers'],
            json['torrent']['snatched']
            )

def group(id):
    json = api.request('torrentgroup', id=id)['response']
    return u'{} - {} ({}) [{}]'.format(
            get_artists(json['group']['musicInfo']),
            json['group']['name'],
            json['group']['year'],
            ', '.join(json['group']['tags'])
            )

def artist(id):
    json = api.request('artist', id=id)['response']
    return u'{} [{}] - Groups: {} Torrents: {} Seeds: {} Leeches: {} Snatches: {}'.format(
            json['name'],
            u', '.join(x['name'] for x in json['tags']),
            json['statistics']['numGroups'],
            json['statistics']['numTorrents'],
            json['statistics']['numSeeders'],
            json['statistics']['numLeechers'],
            json['statistics']['numSnatches']
            )

def thread(threadid):
    json = api.request('forum', type='viewthread', threadid=threadid)['response']
    return u'{} | {} - {}'.format(
            parser.unescape(json['threadTitle']),
            json['forumName'],
            json['posts'][0]['author']['authorName']
            )

def request(id):
    json = api.request('request', id=id)['response']
    return u'{} - {} ({}) [{}] - {}'.format(
            get_artists(json['musicInfo']),
            parser.unescape(json['title']),
            json['year'],
            u', '.join(json['tags']),
            sizeof_fmt(json['totalBounty'])
            )

def get_artists(json):
    artists = json['artists']
    guests = json['with']
    composers = json['composers']
    conductors = json['conductor']
    djs = json['dj']

    if (len(artists) + len(conductors) + len(djs)) == 0 and len(composers) == 0:
        return '';

    val = ''

    if len(composers) == 1:
        val = composers[0]['name']
    elif len(composers) == 2:
        val = u'{} & {}'.format(composers[0]['name'], composers[1]['name'])
    
    if len(composers) > 0 and len(composers) < 3 and len(artists) > 0:
        val += ' performed by '

    composer_str = val

    if len(artists) == 1:
        val += artists[0]['name']
    elif len(artists) == 2:
        val += u'{} & {}'.format(artists[0]['name'], artists[1]['name'])
    elif len(artists) > 2:
        val += 'Various Artists'

    if len(conductors) > 0 and (len(artists) + len(composers)) > 0 and (len(composers) < 3 or len(artists) > 0):
        val += ' under '

    if len(conductors) == 1:
        val += conductors[0]['name']
    elif len(conductors) == 2:
        val += u'{} & {}'.format(conductors[0]['name'], conductors[1]['name'])
    elif len(conductors) > 2:
        val += 'Various Conductors'

    if len(composers) > 0 and (len(artists) + len(conductors)) > 3 and (len(artists) > 0 and len(conductors) > 1):
        val = composer_str + 'Various Artists'
    elif len(composers) > 2 and (len(artists) + len(conductors)) == 0:
        val = 'Various Composers'

    if len(djs) == 1:
        val = djs[0]['name']
    elif len(djs) == 2:
        val = u'{} & {}'.format(djs[0]['name'], djs[1]['name'])
    elif len(djs) > 2:
        val = 'Various DJs'

    return val

def encoding(json):
    val = json['encoding']
    if json['hasLog']:
        val = u'Log ({}%)'.format(json['logScore'])
    if json['hasCue']:
        val += ' Cue'

    return val
