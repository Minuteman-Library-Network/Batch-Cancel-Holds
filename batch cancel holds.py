'''
Jeremy Goldstein
Minuteman Library Network

Script to batch cancel all holds attached to bib records contained in a user specified review file
'''

import requests
import configparser
import json
from base64 import b64encode
import psycopg2
from datetime import datetime
from datetime import timedelta

def get_token():
    # config api    
    config = configparser.ConfigParser()
    config.read('api_info.ini')
    base_url = config['api']['base_url']
    client_key = config['api']['client_key']
    client_secret = config['api']['client_secret']
    auth_string = b64encode((client_key + ':' + client_secret).encode('ascii')).decode('utf-8')
    header = {}
    header["authorization"] = 'Basic ' + auth_string
    header["Content-Type"] = 'application/x-www-form-urlencoded'
    body = {"grant_type": "client_credentials"}
    url = base_url + '/token'
    response = requests.post(url, data=json.dumps(body), headers=header)
    json_response = json.loads(response.text)
    token = json_response["access_token"]
    return token

def runquery(review_file):
#function querries Sierra for the hold.id value of each hold attached to a bib_record in the user entered review file, which must contain bib records

    # import configuration file containing our connection string
    # app.ini looks like the following
    #[db]
    #connection_string = dbname='iii' user='PUT_USERNAME_HERE' host='sierra-db.library-name.org' password='PUT_PASSWORD_HERE' port=1032

    config = configparser.ConfigParser()
    config.read('api_info.ini')
    
    query = """\
			SELECT
			h.id
			FROM
			sierra_view.hold h
			JOIN
			sierra_view.bool_set bs
			ON
			h.record_id = bs.record_metadata_id
			AND bs.bool_info_id = '"""\
			+review_file+"""\
			'"""
      
    conn = psycopg2.connect("dbname='iii' user='" + config['api']['sql_user'] + "' host='" + config['api']['sql_host'] + "' port='1032' password='" + config['api']['sql_pass'] + "' sslmode='require'")

    #Opening a session and querying the database for weekly new items
    cursor = conn.cursor()
    cursor.execute(query)
    #For now, just storing the data in a variable. We'll use it later.
    rows = cursor.fetchall()
    conn.close()
    
    return rows
    
def cancel_hold(hold_id,token):
    config = configparser.ConfigParser()
    config.read('api_info.ini')
    url = config['api']['base_url'] + "/patrons/holds/" + hold_id    
    header = {"Authorization": "Bearer " + token, "Content-Type": "application/json;charset=UTF-8"}
    request = requests.delete(url, headers = header)

def main():
    start_time = datetime.now()
    review_file = raw_input("Enter review file number to search, or type \'q\' to quit.\n")
    while review_file != 'q':
        if not 1 <= int(review_file) <= 652:
            print('Invalid entry, please try again')
            break
        confirm = raw_input("\nThis will cancel all holds attached to bibs contained in review file " + str(review_file) + ".\nDo you wish to proceed?  type \'y\' to continue.\n")
        if not confirm == 'y':
            print('\nThis program will now quit.  Goodbye.')
            break
        query_results = runquery(review_file)
        expiration_time = datetime.now() + timedelta(seconds=3600)
        token = get_token()
        print('\n')
        for rownum, row in enumerate(query_results):
            hold_id = str(row[0])
            print(hold_id)
            if datetime.now() < expiration_time:
                cancel_hold(hold_id,token)
            else:
                print("refreshing token")
                expiration_time = datetime.now() + timedelta(seconds=3600)
                token = get_token()
                cancel_hold(hold_id,token)
        #print("\nThis program will now quit.  Goodbye.")
        review_file = 'q'
                
    print("\nThis program will now quit.  Goodbye.")
    
    
main()
