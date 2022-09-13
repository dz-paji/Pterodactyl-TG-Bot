import configparser
import logging
import telegram
import base
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Dispatcher, MessageHandler, Filters, Updater, CommandHandler, CallbackQueryHandler, PicklePersistence

# Load data from config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Initial bot by Telegram access token
bot = telegram.Bot(token=config['TELEGRAM']['ACCESS_TOKEN'])

# Make the bot presistent
bot_presistent = PicklePersistence(filename='bot_data')

# Create updater and dispatcher
updater = Updater(token=config['TELEGRAM']['ACCESS_TOKEN'], persistence=bot_presistent, use_context=True)
dispatcher = updater.dispatcher

# Default function
def start(update, context):
    context.user_data['api_key'] = 'default'
    context.user_data['url'] = (config['Pterodactyl']['url'])
    content = '''Welcome aboard! Please specify your API KEY using command /set before getting started.
It is worth noting that the Panel has a rate limit(60 rps by default).
You can create an API key from Pterodactyl panel.
Note that the URL for Pterodactyl Panel need to start with https://
Looking for Minecraft server hosting solution? Check out [502Network](https://portal.502.network)!'''
    context.bot.send_message(chat_id=update.effective_chat.id, text=content, parse_mode=ParseMode.MARKDOWN)

# Request function
def get_request(url, api_key):
    attributes = base.react_request(url = url, api_key = api_key)
    return attributes

# Check if api key is set
def check_key(context):
    if context.user_data['api_key'] != 'default':
        return context.user_data['api_key']
    else:
        return 'invalid'

# List all the server
def list_server(update, context):
    url = context.user_data['url'] + 'api/client'
    content = ''

    if check_key(context) == 'inavlid':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Please set your API KEY first.', parse_mode=ParseMode.MARKDOWN)
        return
    else:
        api_key = check_key(context)

    request_raw = get_request(url, api_key)
    server_name = {}

    # Fetch servers
    for i in range(0, len(request_raw)):
        inter_attributes = request_raw[i]
        server_name[inter_attributes['name']] = inter_attributes['identifier']
    for key, value in server_name.items():
        content = content + key + ': `' + value + '`\n'
    content = 'You have the following server: \n' + content

    context.bot.send_message(chat_id=update.effective_chat.id, text=content, parse_mode=ParseMode.MARKDOWN)

# Set the key
def set_key(update, context):
    api_key = update.message.text.partition(' ')[2]
    if len(api_key) == 48:
        context.user_data['api_key'] = api_key
        content = 'You have set the API KEY to: `' + context.user_data['api_key'] + '`'
    else:
        content = 'The API KEY you provided seems invalid. Please check again.'

    context.bot.send_message(chat_id=update.effective_chat.id, text=content, parse_mode=ParseMode.MARKDOWN)

# Set the url
def set_url(update, context):
    url = update.message.text.partition(' ')[2]
    context.user_data['url'] = url
    content = 'Your panel address has been set to: ' + url
    context.bot.send_message(chat_id=update.effective_chat.id, text=content, parse_mode=ParseMode.MARKDOWN)

# Check the status(resource usage)
def status_request(update, context):
    url = context.user_data['url'] + 'api/client/servers/' + update.message.text.partition(' ')[2] + '/utilization'

    if check_key(context) == 'inavlid':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Please set your API KEY first.', parse_mode=ParseMode.MARKDOWN)
        return
    else:
        api_key = check_key(context)

    request_raw = get_request(url, api_key)

    if request_raw['state'] == 'on':
        content = str
        memory_usage = str(int((request_raw['memory']['current'] / request_raw['memory']['limit']) * 100))
        cpu_usage = str(int((request_raw['cpu']['current'] / request_raw['cpu']['limit']) * 100))
        disk_usage = str(int((request_raw['disk']['current'] / request_raw['disk']['limit']) * 100))
        content = 'Server `' + update.message.text.partition(' ')[2] + '`\'s resource utilization: \n Memory usage: `' + memory_usage + '%` \n CPU usage: `' + cpu_usage + '%`\n Disk usage: `' + disk_usage + '%`'
    else:
        content = 'Your server is currently offline.'

    context.bot.send_message(chat_id=update.effective_chat.id, text=content, parse_mode=ParseMode.MARKDOWN)

# Send msg to console
def console_post(update, context):
    if check_key(context) == 'inavlid':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Please set your API KEY first.', parse_mode=ParseMode.MARKDOWN)
        return
    else:
        api_key = check_key(context)

    url = context.user_data['url'] + 'api/client/servers/' + update.message.text.partition(' ')[2].partition(' ')[0] + '/command?command=' + update.message.text.partition(' ')[2].partition(' ')[2]
    response = base.post_request(url, api_key)
    if 'errors' in response:
        if response['errors'][0]['status'] == '412':
            content = 'You need to start the server first before sending any command.'
        else:
            content = response['errors'][0]['code']
    else:
        content = 'Command sent successfully.'
    context.bot.send_message(chat_id=update.effective_chat.id, text=content, phase_mod=ParseMode.MARKDOWN)

# power on function.
def power_on(update, context):
    if check_key(context) == 'inavlid':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Please set your API KEY first.', parse_mode=ParseMode.MARKDOWN)
        return
    else:
        api_key = check_key(context)
    url = context.user_data['url'] + 'api/client/servers/' + update.message.text.partition(' ')[2].partition(' ')[0] + '/power?signal=start'
    response = base.post_request(url, api_key)
    if 'success' in response:
        content = 'Service is now starting..'
    else:
        content = response['errors'][0]['detail']
    context.bot.send_message(chat_id=update.effective_chat.id, text=content, parse_mode=ParseMode.MARKDOWN)

# Just for fun XD
def curse(update, context):
    content = base.get_curse()
    context.bot.send_message(chat_id=update.effective_chat.id, text=content, parse_mode=ParseMode.MARKDOWN)

#Register commands
list_handler = CommandHandler('list', list_server)
dispatcher.add_handler(list_handler)
status_handler = CommandHandler('status', status_request)
dispatcher.add_handler(status_handler)
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
set_key_handler = CommandHandler('set', set_key)
dispatcher.add_handler(set_key_handler)
set_key_handler = CommandHandler('send', console_post)
dispatcher.add_handler(set_key_handler)
set_key_handler = CommandHandler('poweron', power_on)
dispatcher.add_handler(set_key_handler)
set_url_handler = CommandHandler('url', set_url)
dispatcher.add_handler(set_url_handler)
set_url_handler = CommandHandler('curse', curse)
dispatcher.add_handler(set_url_handler)

updater.start_polling()
updater.idle()