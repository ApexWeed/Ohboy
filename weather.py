# coding=utf-8
# Copyright 2008, Sean B. Palmer, inamidst.com
# Copyright 2012, Elsie Powell, embolalia.com
# Licensed under the Eiffel Forum License 2.
from __future__ import unicode_literals, absolute_import, print_function, division

from sopel.module import commands, example, NOLIMIT

import requests
import xmltodict


def woeid_search(query):
    """
    Find the first Where On Earth ID for the given query. Result is the etree
    node for the result, so that location data can still be retrieved. Returns
    None if there is no result, or the woeid field is empty.
    """
    query = 'q=select * from geo.places where text="%s"' % query
    body = requests.get('http://query.yahooapis.com/v1/public/yql?' + query)
    parsed = xmltodict.parse(body.text).get('query')
    results = parsed.get('results')
    if results is None or results.get('place') is None:
        return None
    if type(results.get('place')) is list:
        return results.get('place')[0]
    return results.get('place')


def get_cover(parsed):
    try:
        condition = parsed['channel']['item']['yweather:condition']
    except KeyError:
        return 'unknown'
    text = condition['@text']
    # code = int(condition['code'])
    # TODO parse code to get those little icon thingies.
    return text


def get_temp(parsed):
    try:
        condition = parsed['channel']['item']['yweather:condition']
        temp = int(condition['@temp'])
    except (KeyError, ValueError):
        return 'unknown'
    f = round((temp * 1.8) + 32, 2)
    return (u'%d\u00B0C (%d\u00B0F)' % (temp, f))


def get_humidity(parsed):
    try:
        humidity = parsed['channel']['yweather:atmosphere']['@humidity']
    except (KeyError, ValueError):
        return 'unknown'
    return "Humidity: %s%%" % humidity


def get_wind(parsed):
    try:
        wind_data = parsed['channel']['yweather:wind']
        kph = float(wind_data['@speed'])
        m_s = float(round(kph / 3.6, 1))
        speed = int(round(kph / 1.852, 0))
        degrees = int(wind_data['@direction'])
    except (KeyError, ValueError):
        return 'unknown'

    if speed < 1:
        description = 'Calm'
    elif speed < 4:
        description = 'Light air'
    elif speed < 7:
        description = 'Light breeze'
    elif speed < 11:
        description = 'Gentle breeze'
    elif speed < 16:
        description = 'Moderate breeze'
    elif speed < 22:
        description = 'Fresh breeze'
    elif speed < 28:
        description = 'Strong breeze'
    elif speed < 34:
        description = 'Near gale'
    elif speed < 41:
        description = 'Gale'
    elif speed < 48:
        description = 'Strong gale'
    elif speed < 56:
        description = 'Storm'
    elif speed < 64:
        description = 'Violent storm'
    else:
        description = 'Hurricane'

    if (degrees <= 22.5) or (degrees > 337.5):
        degrees = u'\u2193'
    elif (degrees > 22.5) and (degrees <= 67.5):
        degrees = u'\u2199'
    elif (degrees > 67.5) and (degrees <= 112.5):
        degrees = u'\u2190'
    elif (degrees > 112.5) and (degrees <= 157.5):
        degrees = u'\u2196'
    elif (degrees > 157.5) and (degrees <= 202.5):
        degrees = u'\u2191'
    elif (degrees > 202.5) and (degrees <= 247.5):
        degrees = u'\u2197'
    elif (degrees > 247.5) and (degrees <= 292.5):
        degrees = u'\u2192'
    elif (degrees > 292.5) and (degrees <= 337.5):
        degrees = u'\u2198'

    return description + ' ' + str(m_s) + 'm/s (' + degrees + ')'


@commands('weather', 'wea')
@example('.weather London')
def weather(bot, trigger):
    """.weather location - Show the weather at the given location."""

    location = trigger.group(2)
    woeid = ''
    if not location:
        woeid = bot.db.get_nick_value(trigger.nick, 'woeid')
        if not woeid:
            return bot.msg(trigger.sender, "I don't know where you live. " +
                           'Give me a location, like .weather London, or tell me where you live by saying .setlocation London, for example.')
    else:
        location = location.strip()
        woeid = bot.db.get_nick_value(location, 'woeid')
        if woeid is None:
            first_result = woeid_search(location)
            if first_result is not None:
                woeid = first_result.get('woeid')

    if not woeid:
        return bot.reply("I don't know where that is.")

    query = 'q=select * from weather.forecast where woeid="%s" and u=\'c\'' % woeid
    body = requests.get('http://query.yahooapis.com/v1/public/yql?' + query)
    parsed = xmltodict.parse(body.text).get('query')
    results = parsed.get('results')
    if results is None:
        return bot.reply("No forecast available. Try a more specific location.")
    location = results.get('channel').get('title')
    cover = get_cover(results)
    temp = get_temp(results)
    humidity = get_humidity(results)
    wind = get_wind(results)
    bot.say(u'%s: %s, %s, %s, %s' % (location, cover, temp, humidity, wind))


@commands('setlocation', 'setwoeid')
@example('.setlocation Columbus, OH')
def update_woeid(bot, trigger):
    """Set your default weather location."""
    if not trigger.group(2):
        bot.reply('Give me a location, like "Washington, DC" or "London".')
        return NOLIMIT

    first_result = woeid_search(trigger.group(2))
    if first_result is None:
        return bot.reply("I don't know where that is.")

    woeid = first_result.get('woeid')

    bot.db.set_nick_value(trigger.nick, 'woeid', woeid)

    neighborhood = first_result.get('locality2') or ''
    if neighborhood:
        neighborhood = neighborhood.get('#text') + ', '
    city = first_result.get('locality1') or ''
    # This is to catch cases like 'Bawlf, Alberta' where the location is
    # thought to be a "LocalAdmin" rather than a "Town"
    if city:
        city = city.get('#text')
    else:
        city = first_result.get('name')
    state = first_result.get('admin1').get('#text') or ''
    country = first_result.get('country').get('#text') or ''
    bot.reply('I now have you at WOEID %s (%s%s, %s, %s)' %
              (woeid, neighborhood, city, state, country))
