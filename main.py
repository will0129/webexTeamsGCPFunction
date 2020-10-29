import json
import http.client
import mimetypes
import os


#
#
#
#


#testing Content Filter
import contentFilter



def checkShared(secretKey):
    # The Purpose of this function is to provide a way to check shared secret for webhooks that do not have API Gateway aws strings.

    if os.environ['webhookSecret'] != secretKey:

        internalFailReturn.update([('errorCode', '401'), (
        'errorMessage', 'The Shared Secret provided in the body of the message does not match expectd value')])
        return
    else:
        return




# We Set an internal failure mechanism to respond back to appropriate requests or webhooks
internalFailReturn = {}
from flask import escape
from flask import make_response

def main(event):
    # If we passed the Room ID in the event, we will use that. Otherwise we will source it from environment variable if set.
    # roomID could be set in message by third party apps or IOT devices, or whatnot. Not for webhooks.
    try:
        roomId = event['roomId']
    except:
        roomId = os.environ['teamsRoom']



    internalFailReturn.clear()  # Successive iterations in AWS did not reinstantiate this, we clear this because it would hold errors between API calls.

    # If the message is native (say from IOT Device) we will set message to the message key

    ## this is because GCP doesnt do what AWS does and we have to read the stuff in

    content_type = event.headers['content-type']
    if content_type == 'application/json':
        event_json = event.get_json(silent=True)
        if 'message' in event_json:
            message = event_json['message']

        elif 'organizationUrl' in event_json:
            if event_json['organizationUrl'].find('meraki.com'):
                checkShared(event_json['sharedSecret'])

                message = 'Meraki Log for organization {orgid} on network {netname} : {alertType} : {alertData}'.format(
                    orgid=event_json['organizationId'], netname=event_json['networkName'], alertType=event_json['alertType'],
                    alertData=event_json['alertData'])




        else:
            message = 'can you hear me now'

    ### if any existing logic checks have not created an error, we can send the message to teams.

    if not 'errorCode' in internalFailReturn.keys():
        # if True == True:    # used for debugging
        message2 = message + "event is " + str(event_json)

        teamsAPIKey = os.environ['teamsAPIKey']
        conn = http.client.HTTPSConnection("api.ciscospark.com")
        payload = 'roomId=' + roomId + '&text=' + message
        headers = {
            'Authorization': 'Bearer ' + teamsAPIKey,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        conn.request("POST", "/v1/messages", payload, headers)
        ## After this we need error control, if you get status 200, etc. 

        response = conn.getresponse()
        statuscode = response.status








    if 'errorCode' in internalFailReturn.keys() and 'errorMessage' in internalFailReturn.keys():
        return make_response(str(internalFailReturn['errorMessage']), int(internalFailreturn['errorCode']))
        ### FIX THE ABOVE IF IT WORKS 
    elif statuscode == 200:
        return make_response("the message went to teams", 200)
    elif statuscode == 401:
        return make_response("Error : Auth Failure", 401)
    elif statuscode == 404:
        return make_response("Error : Check URI", 404)
    elif statuscode == 429:
        return make_response("Error : Check rate limits", 429)
    elif statuscode >= 500:
        return make_response("Error : Server", 500)
    else:
        return make_response("Error : Unknown", 500)

       # return {
        #    'statusCode': "200",
         #   'body': "the function ran",
        #}
