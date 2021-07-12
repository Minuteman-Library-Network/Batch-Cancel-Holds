# Batch cancel holds

This script will prompt the user for a valid review file number (in our system a valid integer between 1 and 652)
and then attempt to cancel all holds attached to the bibs within the file via the Delete patrons/holds API endpoint.

Our primary use case for this is to clear out bib records that no longer have any circulating items attached.
Tool as it is currently configured will only identify bib level holds and the user submitted review file number must contain bib records.


Within the dist folder you will find a deployable for windows executable version of the script created using pyinstaller

Prerequistes

In order to function you must complete the api_info.ini file in the same directory
and add your cacert.pem file to the certifi folder

api_info.ini

Requires valid credentials for both the Sierra holds API and sql access
The file should be formatted like so

[api]

base_url = https://[local domain]/iii/sierra-api/v6

client_key = [enter Sierra API key]

client_secret = [enter Sierra API secret]

sql_host = [enter host for Sierra SQL server]

sql_user = [enter sql username]

sql_pass = [enter sql password]

cacert.pem file

To find where this file is located on your computer you may run the following python script

import certifi
certifi.where()

Once you've located the file, copy it to a certifi folder within the same directory
