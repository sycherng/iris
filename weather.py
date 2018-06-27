import asyncio
import discord
import http
import secrets
import urllib
import json

async def respond(bot, message):
    if message.content.startswith(f'{secrets.prefix}weather'):
        await handleWeatherCommand(bot, message)


async def handleWeatherCommand(bot, message):
    '''(Bot, Message) -> None'''
    # try to extract a city from request message
    city = await parseWeatherRequest(message.content)
    if city == None:
        await bot.send_message(message.author, f"Invalid request. Try `{secrets.prefix}weather <city>`.")
        return
 
    # try to get coordinates for the city
    coordinates = await getMajorCityCoordinates(city)
    if coordinates == None:
        await bot.send_message(message.author, f"The supplied city {city} is not supported at this time.")
        return
    (latitude, longitude) = coordinates


    try:
        weather_data = await getWeatherFromApi(latitude, longitude)
        pretty_weather_data = await prettifyWeatherData(weather_data, city)

    except Exception as err:
        await bot.send_message(message.author, f"Something went wrong with your request.\n```{err}```")
        return

    # send the message back to user
    await bot.send_message(message.author, pretty_weather_data)


async def parseWeatherRequest(request_message):
    '''(str) -> str or None
    Command syntax is currently simply `weather city_name`,
    if message length is 2 words as expected, return the second word as city name.'''
    split = request_message.split()
    if len(split) != 2:
        return None
    else:
        return split[1]

     
async def getMajorCityCoordinates(city):
    '''(self) -> tuple or None
    Read from dict mapping major city names to tuples of latitude and longitude.'''
    map_ = secrets.major_city_coordinates
    if city in map_:
        return map_[city]
    else:
        return None


async def getWeatherFromApi(latitude=secrets.latitude, longitude=secrets.longitude, units='ca'):
    '''(str, str, str) -> str
    Fetch weather data from darksky api in the form of json.'''
    conn = http.client.HTTPSConnection("api.darksky.net")
    request_str = f"/forecast/{secrets.dark_sky_API_key}/{latitude},{longitude}"
    params = urllib.parse.urlencode({'units':units, 'exclude':['minutely','flags']})

    conn.request("GET", request_str, params)
    response = conn.getresponse()
    data = response.read()
    decoded_data = data.decode("utf-8")
    data_as_dict = json.loads(decoded_data)
    return data_as_dict


async def prettifyWeatherData(weather_data, city):
    '''(str) -> str'''
    summary = weather_data["currently"]["summary"]
    temperature_F = weather_data["currently"]["temperature"]
    temperature_C = (temperature_F - 32) * 5/9
    return f"Weather in {city} is {summary}, {temperature_C:.2f}C/{temperature_F:.2f}F."
