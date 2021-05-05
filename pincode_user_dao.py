import firebase_admin
from firebase_admin import db
import json

import logging
import time
logging.basicConfig(filename="Log.log",
                    format='[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
                    # take time,level,name
                    datefmt="%d/%b/%Y %H:%M:%S",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

databaseURL ='YOUR URL'
cred_obj = firebase_admin.credentials.Certificate('YOUR JSON')
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL':databaseURL
})

# INSERT USER IN PINCODE
def insertUserToPincode(pincode,user_id,user_name):
    ref = db.reference("/"+pincode)
    dic_pincode_user = ref.get()
    print(dic_pincode_user)
    ref.child('user').push(user_id)
    ref.child('user').push(user_name)
    logger.info("FIREBASE : added new user name : [%s] & user id : [%s] to pincode [%s]" , user_name,user_id, pincode)


#  RETRIVE ALL USER OF PINCODE
def retriveAllUserBasedOnPincode(pincode):
    user = list()
    ref = db.reference("/"+pincode+"/user/")
    dic_pincode_user = ref.get()
    print(dic_pincode_user)
    for key, value in dic_pincode_user.items():
        list.append(value)
    logger.info("FIREBASE : RETURN ALL THE USER OF PINCODE [%s]",pincode)
    return user

# RETRIVE ALL PINCODE
def retriveAllPincode():
    listPincode = list()
    ref = db.reference("/")
    pincode = ref.get()
    for key, value in pincode.items():
        listPincode.append(key)
    logger.info("FIREBASE : RETRIVED ALL PINCODE")
    return listPincode