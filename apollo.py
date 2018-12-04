import sopel.module
import collections
import whatapi
import HTMLParser
import urlparse
import re
import cPickle as pickle
import os
import datetime
import requests
from subprocess import call

helptext = collections.namedtuple('HelpText', 'perms command line')

api = None
parser = HTMLParser.HTMLParser()
regex = re.compile(r"(?u)https://(?:[^\.]+\.)?orpheus.network/(.*?)\.php\??([-a-zA-Z0-9@:%_\+.~#?&//=]*)")
sudoer = ''
sudotime = datetime.datetime.utcnow()
sudocount = 0

class ApolloSection(sopel.config.types.StaticSection):
    username = sopel.config.types.ValidatedAttribute('username')
    password = sopel.config.types.ValidatedAttribute('password')
    server = sopel.config.types.ValidatedAttribute('server')
    api = sopel.config.types.ValidatedAttribute('api', bool, default=False)
    tracker = sopel.config.types.ValidatedAttribute('tracker')
    cookie_file = sopel.config.types.FilenameAttribute('cookie_file', relative=False)
    simulate = sopel.config.types.ValidatedAttribute('simulate', bool, default=False)
    apollo_config = sopel.config.types.FilenameAttribute('apollo_config', relative=True)
    status_channel = sopel.config.types.ValidatedAttribute('status_channel')
    check_status = sopel.config.types.ValidatedAttribute('check_status', bool, default=False)
    status_format = sopel.config.types.ValidatedAttribute('status_format', str, default='Status - SITE {} / TRACKER {} / ANNOUNCE {} / IRC UP / BOT {}')
    bot = sopel.config.types.ValidatedAttribute('bot')
    bot_channel = sopel.config.types.ValidatedAttribute('bot_channel')

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
    config.apollo.configure_setting('api', 'Whether to enable API')
    config.apollo.configure_setting('tracker', 'Tracker URL to check')
    config.apollo.configure_setting('cookie_file', 'File to store Apollo session data')
    config.apollo.configure_setting('simulate', 'Whether to allow simulation')
    config.apollo.configure_setting('apollo_config', 'Path to config for apollo simulator')
    config.apollo.configure_setting('status_channel', 'The channel to annouce status in')
    config.apollo.configure_setting('check_status', 'Whether to check apollo status')
    config.apollo.configure_setting('status_format', 'Format to output status')
    config.apollo.configure_setting('bot', 'Name of the bot to check')
    config.apollo.configure_setting('bot_channel', 'Channel the bot idles in')

def setup(bot):
    global api
    bot.config.define_section('apollo', ApolloSection)

    try:
        if bot.config.apollo.api == True and api == None:
            if os.path.isfile(bot.config.apollo.cookie_file):
                try:
                    cookies = pickle.load(open(bot.config.apollo.cookie_file, 'rb'))
                    api = whatapi.WhatAPI(username=bot.config.apollo.username, password=bot.config.apollo.password, server=bot.config.apollo.server, cookies=cookies)
                except:
                        api = whatapi.WhatAPI(username=bot.config.apollo.username, password=bot.config.apollo.password, server=bot.config.apollo.server)
            else:
                api = whatapi.WhatAPI(username=bot.config.apollo.username, password=bot.config.apollo.password, server=bot.config.apollo.server)
    except:
        api = None

    if not bot.memory.contains('help'):
        bot.memory['help'] = sopel.tools.SopelMemory()

    bot.memory['help']['apollo'] = sopel.tools.SopelMemory()
    bot.memory['help']['apollo']['short'] = 'Feature parity with APOLLO'
    bot.memory['help']['apollo']['long'] = {
            helptext('all', '!sandwich', 'Requests a sandwich'),
            helptext('all', '!slap <target>', 'Slaps somebody around'),
            helptext('all', '!apollo stats', 'Prints site stats'),
            helptext('all', '!apollo user <id>', 'Prints user info'),
            helptext('all', '!apollo user <name>', 'Prints user search results'),
            helptext('all', '!apollo loadavg', 'Prints loadavg for some reason'),
            helptext('all', '!apollo top10 torrents day|week|overall|snatched|data|seeded', 'Searches torrent top 10'),
            helptext('all', '!apollo top10 tags ut|ur|v', 'Searches tag top 10'),
            helptext('all', '!apollo top10 users ul|dl|numul|uls|dls', 'Searches user top 10'),
            helptext('admin', '!sudoslap <count> <target>', 'Slaps somebody around. A bunch'),
            helptext('admin', '!sudosandwich', 'Requests a sandwich'),
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
    if 'apollo' in bot.config.core.host:
        return

    if trigger.group(2):
        bot.say(trigger.nick + ' slaps ' + trigger.group(2))

@sopel.module.commands('sandwich')
def sandwich(bot, trigger):
    if 'apollo' in bot.config.core.host:
        return

    bot.say('Make it yourself, ' + trigger.nick)

@sopel.module.commands('sudosandwich')
def sudosandwich(bot, trigger):
    if 'apollo' in bot.config.core.host:
        return

    if trigger.admin:
        bot.say('Here you go, ' + trigger.nick + ' [sandwich]')
    else:
        global sudoer
        global sudotime
        global sudocount
        sudoer = trigger.nick
        sudotime = datetime.datetime.utcnow()
        sudocount = 0
        bot.say("[sudo] password for {0}".format(trigger.nick))

@sopel.module.rule(r'.*')
def sudo(bot, trigger):
    global sudoer
    global sudocount
    if trigger.nick == sudoer and (datetime.datetime.utcnow() - sudotime).total_seconds() <= 60:
        if trigger.group(0) == 'hunter2':
            bot.say("Here you go, {0} [sandwich]".format(trigger.nick))
        else:
            sudocount = sudocount + 1
            if sudocount < 3:
                bot.say("Sorry, try again.")
            else:
                bot.say("sudo: {0} incorrect password attempt".format(str(sudocount)))
                sudoer = ''

@sopel.module.commands('sudoslap')
def sudoslap(bot, trigger):
    if 'apollo' in bot.config.core.host:
        return

    if not trigger.admin or not trigger.group(3) or not trigger.group(4):
        bot.say("<workstations> no witty comment? :P")
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

status_regex = r'Status - SITE ([a-zA-Z]*) \/ TRACKER ([a-zA-Z]*) \/ ANNOUNCE ([a-zA-Z]*) \/ IRC ([a-zA-Z]*) \/ BOT ([a-z[A-Z]*)'

@sopel.module.interval(60)
def isup(bot):
    if bot.config.apollo.check_status:
        if bot.config.apollo.status_channel in bot.channels:
            r = requests.get(bot.config.apollo.server)
            #site_status = 'up' if r.status_code == 200 else 'down'
            site_status = str(r.status_code)
            r = requests.get(bot.config.apollo.tracker)
            #tracker_status = 'up' if r.status_code == 200 else 'down'
            tracker_status = str(r.status_code)
            bot_status = '200' if bot.config.apollo.bot.lower() in bot.channels[bot.config.apollo.bot_channel.lower()].users else '400'
            announce_status = '200' if bot_status == '200' and site_status == '200' else '400'
            chan = bot.channels[bot.config.apollo.status_channel]
            status = bot.config.apollo.status_format.format(site_status.upper(), tracker_status.upper(), announce_status.upper(), bot_status.upper())

            if status != chan.topic:
                bot.write(('TOPIC', bot.config.apollo.status_channel, ':{}'.format(status)))
                bot.say('Changed: {}'.format(status), bot.config.apollo.status_channel) 

@sopel.module.commands('u')
def u(bot, trigger):
    if not api:
        return

    if not trigger.group(3):
        bot.say(user(trigger.nick))
    else:
        bot.say(user(trigger.group(3)))

@sopel.module.commands('apollo')
def apollo(bot, trigger):
    command = trigger.group(3)
    args = trigger.group(2)[len(trigger.group(3)) + 1:]

    if command == 'status':
        if bot.config.apollo.check_status and bot.config.apollo.status_channel in bot.channels:
            bot.say(bot.channels[bot.config.apollo.status_channel].topic)
            return
    
    if not api:
        return

    if command == 'user':
        if not trigger.group(4):
            bot.say(user(trigger.nick))
        else:
            bot.say(user(args))
    elif command == 'stats':
        json = api.request('stats')
        bot.say(u'Users: {}/{} ({} D / {} W / {} M) Torrents: {} Releases: {} Artists: {} Perfects: {} Reqs: {}/{} S/L: {}/{}'.format(
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
                        parser.unescape(s_user['username']),
                        s_user['id'],
                        s_user['numUploads'],
                        sizeof_fmt(s_user['uploaded']),
                        sizeof_fmt(s_user['upSpeed']),
                        sizeof_fmt(s_user['downloaded']),
                        sizeof_fmt(s_user['downSpeed']),
                        s_user['joinDate']
                        ))

def title(bot, trigger, match):
    if not api:
        return

    args = dict(urlparse.parse_qsl(urlparse.urlparse(match.group(0)).query))
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
    elif match.group(1) == 'collages':
        if 'id' in args:
            return collage(args['id'])
        else:
            return 'Apollo - Collages'
    else:
        return 'Apollo'

def user(id):
    if not id.isdigit():
        json = api.request('usersearch', search=id)
        if len(json['response']['results']) == 1:
            id = json['response']['results'][0]['userId']
        else:
            return u'Results: {}'.format(', '.join([u'{} ({})'.format(s_user['username'], s_user['userId']) for s_user in json['response']['results']]))

    
    json = api.request('user', id=id)['response']
    return u'{} ({}): {} U {} D ({}) joined {} last seen {}, ranks: UL {} DL {} UP {} Req {} Bounty {} Posts {} Artists {} Overall {}'.format(
            parser.unescape(json['username']),
            parser.unescape(json['personal']['class']),
            sizeof_fmt(json['stats']['uploaded'] or 0),
            sizeof_fmt(json['stats']['downloaded'] or 0),
            json['stats']['ratio'],
            json['stats']['joinedDate'],
            json['stats']['lastAccess'] or 'being paranoid',
            json['ranks']['uploaded'] or 0,
            json['ranks']['downloaded'] or 0,
            json['ranks']['uploads'] or 0,
            json['ranks']['requests'] or 0,
            json['ranks']['bounty'] or 0,
            json['ranks']['posts'] or 0,
            json['ranks']['artists'] or 0,
            json['ranks']['overall'] or 0
            )

def torrent(id):
    json = api.request('torrent', id=id)['response']
    if json['group']['categoryName'] == 'Music':
        return u'{} - {} ({}) [{} - {} ({})] [{}] Seeds: {} Leeches: {} Snatches: {}'.format(
                get_artists(json['group']['musicInfo']),
                parser.unescape(json['group']['name']),
                json['group']['year'],
                json['torrent']['media'],
                json['torrent']['format'],
                encoding(json['torrent']),
                parser.unescape(', '.join(json['group']['tags'][:10])),
                json['torrent']['seeders'],
                json['torrent']['leechers'],
                json['torrent']['snatched']
                )
    else:
        return u'{} [{}] Seeds: {} Leeches: {} Snatches: {}'.format(
                parser.unescape(json['group']['name']),
                parser.unescape(', '.join(json['group']['tags'][:10])),
                json['torrent']['seeders'],
                json['torrent']['leechers'],
                json['torrent']['snatched']
                )

def group(id):
    json = api.request('torrentgroup', id=id)['response']
    return u'{} - {} ({}) [{}] Seeds: {} Leeches: {} Snatches: {}'.format(
            get_artists(json['group']['musicInfo']),
            parser.unescape(json['group']['name']),
            json['group']['year'],
            parser.unescape(', '.join(json['group']['tags'][:10])),
            sum(x['seeders'] for x in json['torrents']),
            sum(x['leechers'] for x in json['torrents']),
            sum(x['snatched'] for x in json['torrents'])
            )

def artist(id):
    json = api.request('artist', id=id)['response']
    tags = ''
    if json['tags'] and isinstance(json['tags'], (dict)):
        tags = parser.unescape(u', '.join((x['name'] for x in json['tags'])[:10]))
    return u'{} [{}] - Groups: {} Torrents: {} Seeds: {} Leeches: {} Snatches: {}'.format(
            parser.unescape(json['name']),
            tags,
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
            parser.unescape(json['forumName']),
            parser.unescape(json['posts'][0]['author']['authorName'])
            )

def request(id):
    json = api.request('request', id=id)['response']
    return u'{} - {} ({}) [{}] - {}'.format(
            get_artists(json['musicInfo']),
            parser.unescape(json['title']),
            json['year'],
            parser.unescape(u', '.join(json['tags'])),
            sizeof_fmt(json['totalBounty'])
            )

def collage(id):
    json = api.request('collage', id=id)['response']
    return u'{} collage: {}, {} torrents'.format(
            parser.unescape(json['collageCategoryName']),
            parser.unescape(json['name']),
            len(json['torrentGroupIDList'])
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

    return parser.unescape(val)

def encoding(json):
    val = json['encoding']
    if json['hasLog']:
        val = u'Log ({}%)'.format(json['logScore'])
    if json['hasCue']:
        val += ' Cue'

    return val
