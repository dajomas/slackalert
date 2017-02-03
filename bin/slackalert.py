#!/opt/splunk/bin/python

# Author: Johan Godfried (johan@goditt.com)
# version 0.3
# Changelog
# - removed support for conf file
# - removed support for cli argument handling
# + add support for configuration settings from STDIN
# + add check for channel name starting with # or @ (default to # if neither)
# version 0.2
# ChangeLog
# + Add cli argument handling

import os
import sys
import time
import getopt
import requests
import json
import ConfigParser
import gzip
import csv
 
# initialize the configuration dictionary
conf = {}
res_data = {}
additional_fields = []
alerttype = ""
channel_name = ""
message = ""
splunk_alert = ""

def get_value(value_name):
    # Is there a result field defined for this value
    fieldname = None
    try:
        fieldname = conf["default"][value_name+"_fld"]
    except:
        pass
        
    # Extract the field from the search result
    value = None
    if fieldname != None:
        try:
            value = res_data[fieldname]
        except:
            value = None

    if value == None:
        # Is there an entry for the field in the configuration?
        try:
            value = conf["default"][value_name]
        except:
            # Nope
            value = None

    return value
            
def send_message():
    # generate the payload
    slackpayload = {}
    for field in ['username','icon_emoji','icon_url','channel']:
        fld_value = get_value(field)
        if fld_value != None:
            if field == 'channel':
                channel_name = fld_value
                # Check to see if the channel_name starts with an # (channel) or @ (person)
                if channel_name[0] != "#" and channel_name[0] != "@":
                   # If neither we default to a channel
                   channel_name = "#"+channel_name
                slackpayload[field] = channel_name
            else:
                slackpayload[field] = fld_value

    # based on the alerttype, set the bar color
    atcol = None
    atdef = get_value("alerttype_defaut")
    if atdef == None:
        atdef = "#000000"
    alerttype = get_value("alerttype")
    alertmsg = get_value("message")
    # collect alerttypes and colors
    atcols = json.loads(get_value("alerttype_list"))
    if atcols != None:
        for conf_alerttype in atcols:
            if conf_alerttype.lower() == alerttype.lower():
                # collect the color for the current allerttype
                atcol = atcols[conf_alerttype]

    # if no color for the current alerttype has been found, use the default color
    if atcol == None:
        atcol = atdef

    # Add fields for payload
    allfields = []
    allfields.append( { 'title': 'ALERT', 'value': '', 'short': 'true' } )
    allfields.append( { 'title': '', 'value': alerttype, 'short': 'true' } )
    allfields.append( { 'title': 'MESSAGE', 'value': '', 'short': 'false' } )
    allfields.append( { 'title': '', 'value': alertmsg, 'short': 'false' } )
    for field in additional_fields:
        allfields.append(field)

    payloadatt = [
        {
            'color': atcol,
            'fields': allfields
        }
    ]
    for field in ['title','fallback','channel','pretext','text','author_name','author_link','author_icon','title_link','image_url','thumb_url','footer','footer_icon','ts']:
        field_val = get_value(field)
        if field_val != None and field_val != "":
            payloadatt[0][field] = field_val

    slackpayload['attachments'] = payloadatt
    
    # Send the payload to the slack incoming webhook
    slackurl = get_value("url")
    slacktoken = get_value("hooktoken")
            
    if slackurl != None and slacktoken != None:
        proxy = get_value("proxy")
        proxies = {}
        if proxy != None and proxy != "":
            proxies = {'http': proxy, 'https': proxy,}
            req_res = requests.post(slackurl+"/"+slacktoken,data=json.dumps(slackpayload),proxies=proxies)
        else:
            req_res = requests.post(slackurl+"/"+slacktoken,data=json.dumps(slackpayload))
    else:
        sys.exit(1)
        
    # Print the result text
    print(req_res.text)

def process_alert():
    try:
        conf_additional_fields = json.loads(conf["default"]["additional_fields"])
        for fld in conf_additional_fields:
            # generate the additional alert fields
            additional_fields.append( { 'title': fld, 'value': '', 'short': 'true' } )
            additional_fields.append( { 'title': '', 'value': conf_additional_fields[fld], 'short': 'true' } )
    except KeyError as e:
        # no additional alert fields found
        pass

    # Extract the fields that are mandatory from the search result
    alerttype = get_value('alerttype')
    message = get_value('message')
    if alerttype == None or message == None:
        print("One of the mandatory fields (alerttype or message) is not found in the search results")
        sys.exit(1)

if __name__ == '__main__':
    # Process Splunk provided arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        payload = json.loads(sys.stdin.read())
        conf["default"] = payload.get('configuration')
        res_data = payload["result"]
        splunk_alert = payload["search_name"]

        # Process settings for current alert
        process_alert()
        # Finally send the message
        send_message()
