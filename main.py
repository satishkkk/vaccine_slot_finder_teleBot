import configparser as cfg
import json
import logging
import time
import demoji
import requests
from requests import HTTPError
from telegram import *;
from telegram.ext import *;

logging.basicConfig(filename="Log.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    # take time,level,name
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def read_token_from_config_file(config):
    parser = cfg.ConfigParser()
    parser.read(config)
    return parser.get('creds', 'token')


token = read_token_from_config_file('config.cfg')
bot = Bot(token)
pincode_user_map = {}


def start(update, context: CallbackContext):
    name = update.message.from_user.first_name  # first name of the user messaging
    chat_id = update.message.chat_id
    logger.info("User name: %s , CHAT ID: %s", name, chat_id)
    reply = "Hi!! {} , add your pincode".format(name)
    bot.send_message(chat_id=update.message.chat_id, text=reply)  # sending messag

def validate_pin(pin):
    return len(pin)==6 and pin.isdigit()

def get_pincode(update, context: CallbackContext):
    pincode = update.message.text.encode()
    if(validate_pin(pincode)):
        reply = "You entered {} , we will notify you once we found slot for you.".format(pincode.decode())
        logger.info("%s entered %s , pincode", update.message.from_user.first_name, pincode)

        if pincode in pincode_user_map:  # pin code exist
            pincode_user_map[pincode].append(update.message.chat_id)
        else:  # add new pin code
            pincode_user_map[pincode] = [update.message.chat_id]

        bot.send_message(chat_id=update.message.chat_id, text=reply)
    else:
        logger.info("%s entered %s , pincode", update.message.from_user.first_name, pincode)
        bot.send_message(chat_id=update.message.chat_id, text="Thanks "+update.message.from_user.first_name+" , we are expecting valid pin code")


def error(update, context: CallbackContext):
    logger.error("Shit!! Update {} caused error {}".format(update, update.error))


def getVaccineData():
    while True:
        for pincode in pincode_user_map:
            logger.info("Fetching data for pincode: %s", pincode)
            out = fetchData(pincode, 'dummydate')
            if (out != "No Slots"):
                for user in pincode_user_map[pincode]:
                    bot.send_message(user, text="Response : " + out)
            time.sleep(60)

def fetchData(pincode, date):
    date = '02-05-2021'
    url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode=' + pincode + '&date=' + date
    headers = {
        'accept': 'application/json', 'Accept-Language': 'hi_IN',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
        if (response.status_code == 200):
            jsonResponse = response.json()
            logger.info("Fetching data for pincode: %s", pincode)
            logger.info("Response: %s", jsonResponse)
            if (len(jsonResponse['sessions']) != 0):
                return json.dump(jsonResponse)
            else:
                return "No Slots"
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')


def main():
    print("Bot Started")

    # Create the Updater and pass it your bot's token.
    updater = Updater(read_token_from_config_file('config.cfg'), use_context=True)
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    # start_value = CommandHandler('test', getVaccineData)
    # dispatcher.add_handler(start_value)
    dispatcher.add_handler(MessageHandler(Filters.text, get_pincode))  # if the user sends text
    dispatcher.add_error_handler(error)

    updater.start_polling()
    getVaccineData()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
