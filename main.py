import configparser as cfg
import json
import logging
import time
import datetime
import requests
from requests import HTTPError
from telegram import *;
from telegram.ext import *;
import os;
#
# logging.basicConfig(filename="Log.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     # take time,level,name
#                     level=logging.INFO)

logging.basicConfig( format='[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
                    # take time,level,name
                    datefmt="%d/%b/%Y %H:%M:%S",
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
        pincode = pincode.decode()
        reply = "You entered {} , we will notify you once we found slot for you.".format(pincode)
        logger.info("%s entered %s , pincode", update.message.from_user.first_name, pincode)

        if pincode in pincode_user_map:  # pin code exist
            pincode_user_map[pincode].append(update.message.chat_id)
        else:  # add new pin code
            pincode_user_map[pincode] = [update.message.chat_id]

        bot.send_message(chat_id=update.message.chat_id, text=reply)
    else:
        logger.info("%s entered %s , pincode", update.message.from_user.first_name, pincode.decode())
        bot.send_message(chat_id=update.message.chat_id, text="Thanks "+update.message.from_user.first_name+" , we are expecting valid pin code")
    logger.info("pincode_user_map size: %s ", len(pincode_user_map))


def error(update, context: CallbackContext):
    logger.error("Shit!! Update {} caused error {}".format(update, update.error))


def getVaccineData():

    while True:
        try:
            for pincode in pincode_user_map.copy():
                date = datetime.datetime.now()
                for i in range(10):
                    date += datetime.timedelta(days=1)
                    formated_date = date.strftime("%d-%m-%y")
                    logger.info("Fetching data for pincode: %s and date %s", pincode,formated_date)
                    out = fetchData(pincode, formated_date)
                    if (out != "No Slots"):
                        for user in pincode_user_map[pincode]:
                            bot.send_message(user, text="Response : " + out)
                    else:
                        logger.info("No slots found for pincode: %s and %s ", pincode, formated_date)
                time.sleep(120) # sleep for 2 min after finding  each pin code
        except Exception as err:
            print(f'Other error occurred: {err}')

def fetchData(pincode, date):
    url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode=' + str(pincode) + '&date=' + str(date)
    headers = {
        'accept': 'application/json', 'Accept-Language': 'hi_IN',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    try:
        logger.info("url : %s ", url)
        response = requests.get(url, headers=headers)
        if (response.status_code == 200):
            jsonResponse = response.json()
            logger.info("Response: %s", jsonResponse)
            if (len(jsonResponse['sessions']) != 0):
                logger.info("Slot found for pincode %s",pincode)
                return json.dump(jsonResponse)
            else:
                return "No Slots"
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')


def main():
    print("Bot Started")

    TOKEN =read_token_from_config_file('config.cfg')
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN, use_context=True)
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    # start_value = CommandHandler('test', getVaccineData)
    # dispatcher.add_handler(start_value)
    dispatcher.add_handler(MessageHandler(Filters.text, get_pincode))  # if the user sends text
    dispatcher.add_error_handler(error)

    updater.start_polling()
    getVaccineData()
    updater.idle()


if __name__ == "__main__":
    main()
