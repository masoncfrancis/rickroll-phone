from flask import Flask, request, redirect, send_file
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import json
import openai
import mysql.connector

def commandProc(textArray, twilioAut, dbCursor=None):
    client = Client(twilioAuth['accountsid'], twilioAuth['authtoken'])
    phoneNum = "+1" + textArray[1]
    if textArray[0][1:] == "rickroll":
        call = client.calls.create(
                        url="https://8f7c-206-174-165-139.ngrok.io/rickrollmusic",
                        to=phoneNum,
                        from_='+18013493494'
                    )
    elif textArray[0][1:] == "deletehistory":


app = Flask(__name__)

@app.route("/")
def hello():
  return "Stop trying to break in to my server"

@app.route("/rickrollmusic", methods=['GET', 'POST'])
def getmusic():
  return send_file('static/music.mp3')

@app.route("/yeet")
def yeet():
    return "yeetus"

@app.route("/rejection", methods=['GET', 'POST'])
def rejection():

    # get needed auth info

    file = open("accountinfo.json")
    info = json.load(file)
    file.close()
    
    phoneFile = open("phonenumbers.json")
    phone = json.load(phoneFile)
    phoneFile.close()

    openAiInfoFile = open("openaiauth.json")
    openai.api_key = json.load(openAiInfoFile)['key']
    openAiInfoFile.close()

    dbInfoFile = open("db.json")
    dbInfo = json.load(dbInfoFile)
    dbInfoFile.close()

    # connect to db
    dbConn = mysql.connector.connect(
        host=dbInfo['address'],
        user=dbInfo['user'],
        password=dbInfo['password']
    )
    dbCursor = dbConn.cursor()

    # get message info
    receivedText = request.values.get('Body', None)
    phoneNumber = request.values.get('From', None)

    # check for commands
    if receivedText[0] == "#":
        commandProc(receivedText.split(), info, dbCursor)
    else:

        # get message reply from OpenAI API
        prompt = "Pretend to be a person who just exchanged phone numbers with the person texting you. You are somewhat romantically interested in the person texting you. Your ultimate objective is to convince the other person to call you soon instead of text. Your phone has some problems, so they must call you. You cannot call them. Your phone also has problems with picture messages, so you cannot send or receive them. Don't ask the person to call you on the first message you send to them. Never guess or use the person's name. Language style should be very casual and somewhat flirtatious, in the style of a young adult in their early twenties. Responses should be in the form of a text message. The human will message first and you should respond with just one text message. AI responses should not have a prefix indicating that AI is talking. The human will speak first in this dialogue."

        getQuery = f"SELECT * FROM rejection.openaitest WHERE phoneNumber ='{phoneNumber}' ORDER BY timeGenerated DESC"

        dbCursor.execute(getQuery)

        getResult = dbCursor.fetchone()
        secondResult = dbCursor.fetchone()
        throwAway = dbCursor.fetchall()
        if getResult == None:
            prompt = prompt + " \n\n" + receivedText + " \n\n"
        else:
            prompt = getResult[2] + " \n\n" + getResult[3] + "\n\n" + receivedText + " \n\n"
        

        openAiResponse = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.5,
            max_tokens=60,
            top_p=1,
            frequency_penalty=0.5,
            presence_penalty=0
        )

        #insert OpenAI reply into db
        query = "INSERT INTO rejection.openaitest (id, timeGenerated, prompt, outgoingText, phoneNumber) VALUES (NULL, CURRENT_TIMESTAMP, %s, %s, %s)"
        values = (prompt, openAiResponse['choices'][0]['text'].lstrip('\t\n\r'), phoneNumber)
        dbCursor.execute(query, values)
        dbConn.commit()

        # send message
        client = Client(info['accountsid'], info['authtoken'])

        message = client.messages.create(
                                    body=openAiResponse['choices'][0]['text'].lstrip('\t\n\r'),
                                    from_=phone["from"],
                                    to=phoneNumber
                                )

        return message.sid
    return ""

@app.route("/sms", methods=['GET', 'POST'])
def sms():

    resp = MessagingResponse()

    # Add a message
    resp.message("YeetStreet")

    return str(resp)

if __name__ == "__main__":
  app.run()
