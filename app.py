from flask import Flask, request, redirect
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import json

app = Flask(__name__)

@app.route("/")
def hello():
  return "Hello World!"

@app.route("/yeet")
def yeet():
    return "yeetus"

@app.route("/rejection", methods=['GET', 'POST'])
def rejection():
    file = open("accountinfo.json")
    info = json.load(file)
    phone = json.load(open("phonenumbers.json"))


    account_sid = info['accountsid']
    auth_token = info['authtoken']
    client = Client(account_sid, auth_token)

    message = client.messages.create(
                                body='Yeet',
                                from_=phone["from"],
                                to=phone["to"]
                            )

    return message.sid

@app.route("/sms", methods=['GET', 'POST'])
def sms():

    resp = MessagingResponse()

    # Add a message
    resp.message("YeetStreet")

    return str(resp)

if __name__ == "__main__":
  app.run()