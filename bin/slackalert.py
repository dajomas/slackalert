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
import getopt
import datetime
 
# initialize the configuration dictionary
conf = {}
all_res_data = {}
additional_fields = []
alerttype = ""
channel_name = ""
message = ""
splunk_alert = ""

do_execute = 0
do_debug = 0
do_pretty = 0
no_send = 0

def debug_print(debug_msg, txt_to_print):
    if do_debug == 1:
        print "***********************"
        print datetime.datetime.now().strftime("* %Y-%m-%d %H:%M:%S *")
        print "***********************"
        print debug_msg
        print "***********************"
        if do_pretty == 1:
            try:
                print json.dumps(txt_to_print, indent=4, sort_keys=True)
            except:
                print txt_to_print
        else:
            print txt_to_print

def replace_macro(txtstring, res_data):
    for key in res_data.keys():
        try:
            txtstring = txtstring.replace('{'+key+'}',res_data[key][0])
        except:
            pass
            
    return txtstring
    

def get_value(value_name, res_data=None):
    value = None
    if res_data != None:
        # Is there a result field defined for this value
        fieldname = None
        try:
            fieldname = conf["default"][value_name+"_fld"]
        except:
            pass
            
        # Extract the field from the search result
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

    if res_data != None:
        return replace_macro(value, res_data)
    else:
        return value
            
def send_message():

    # generate the payload
    slackpayload = {}
    for field in ['username','icon_emoji','icon_url']:
        fld_value = get_value(field)
        if fld_value != None:
            slackpayload[field] = fld_value

    atdef = get_value("alerttype_defaut")
    if atdef == None:
        atdef = "#000000"
    atcols = json.loads(get_value("alerttype_list"))

    channel_name = get_value("channel")
    # Check to see if the channel_name starts with an # (channel) or @ (person)
    if channel_name != None:
        if channel_name[0] != "#" and channel_name[0] != "@":
            # If neither we default to a channel
            channel_name = "#"+channel_name
        slackpayload[field] = channel_name

    slackpayload['attachments'] = []
    for res_data in all_res_data:
        debug_print("res_data", res_data)
        # based on the alerttype, set the bar color
        atcol = None
        alerttype = get_value("alerttype", res_data)
        alertmsg = get_value("message", res_data)
        if alerttype == None or alertmsg  == None:
            print("One of the mandatory fields (alerttype or message) is not found in the search results")
            sys.exit(1)

        # collect alerttypes and colors
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
        try:
            conf_additional_fields = json.loads(conf["default"]["additional_fields"])
            for fld in conf_additional_fields:
                # generate the additional alert fields
                allfields.append( { 'title': fld, 'value': '', 'short': 'true' } )
                allfields.append( { 'title': '', 'value': replace_macro(conf_additional_fields[fld], res_data), 'short': 'true' } )
        except KeyError as e:
            # no additional alert fields found
            pass
    
        payloadatt = {
            'color': atcol,
            'fields': allfields
        }

        for field in ['title','fallback','channel','pretext','text','author_name','author_link','author_icon','title_link','image_url','thumb_url','footer','footer_icon','ts']:
            field_val = get_value(field)
            if field_val != None and field_val != "":
                payloadatt[field] = field_val
    
        debug_print("payloadatt", payloadatt)
        slackpayload['attachments'].append(payloadatt)
    
    # Send the payload to the slack incoming webhook
    slackurl = get_value("url")
    slacktoken = get_value("hooktoken")

    debug_print("slackpayload", slackpayload)
    debug_print("slackurl", slackurl)
    debug_print("slacktoken", slacktoken)
            
    if slackurl != None and slacktoken != None:
        proxy = get_value("proxy")
        proxies = {}
        if proxy != None and proxy != "":
            proxies = {'http': proxy, 'https': proxy,}
            debug_print("proxies", proxies)
            if no_send != 1:
                req_res = requests.post(slackurl+"/"+slacktoken,data=json.dumps(slackpayload),proxies=proxies)
        else:
            if no_send != 1:
                req_res = requests.post(slackurl+"/"+slacktoken,data=json.dumps(slackpayload))
    else:
        sys.exit(1)
        
    # Print the result text
    if no_send != 1:
        print(req_res.text)

def read_res_file(fname):
    read_res_data = []
    with gzip.open(fname) as f:
        reader = csv.DictReader(f)
        for row in reader:
            read_res_data.append(row)

    debug_print("read_res_data", read_res_data)
    return read_res_data

if __name__ == '__main__':

    try:
        opts, args = getopt.getopt(sys.argv[1:],"edpn",["execute","debug","pretty","nosend"])
    except getopt.GetoptError:
        print "slackalert.py [-e|--execute] [-d|--debug] [-p|--pretty] [-n|--nosend]"
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-e' or opt == '--execute':
            do_execute = 1
        elif opt == '-d' or opt == '--debug':
            do_debug = 1
        elif opt == '-p' or opt == '--pretty':
            do_pretty = 1
        elif opt == '-n' or opt == '--nosend':
            no_send = 1
    # Process Splunk provided arguments

    if do_execute == 1:
        payload = json.loads(sys.stdin.read())
        debug_print("payload", payload)
        conf["default"] = payload.get('configuration')
        debug_print("configuration", conf["default"])
        all_res_data = read_res_file(payload["results_file"])
        debug_print("all_res_data", all_res_data)
        splunk_alert = payload["search_name"]

        # Finally send the message
        send_message()
