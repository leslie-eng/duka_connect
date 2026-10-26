import requests
import json
import pandas as pd


USERS_API = "https://jsonplaceholder.typicode.com/users"

# every api needs a try and except block
try:
    response = requests.get(USERS_API)
    #print(response.json())
except Exception as e:
    print("The connection wasn't successful and the error was {e}")

"""
The response was a list with dictionaries
"""

# extract names, emails, cities, and companies
# step 1: access one value in the list

raw = response.json()

# the extracted values should be stored in an empty list
raw_data = []
user = dict

# step 2: loop through the list and access the required headers
# store the extracted values in dictionaries then append them into a list

for i in range(0, len(raw)):
    user = {
        'name': raw[i]['name'],
        'email': raw[i]['email'],
        'city' : raw[i]['address']['city'],
        'company': raw[i]['company']['name']
    }
    raw_data.append(user)
    
# check the data has been extracted and the count is 10
print(raw_data)
print(len(raw_data))

# transform the raw_data into a dataframe
df = pd.DataFrame(raw_data)
print(df)

# export the dataframe into a csv
df.to_csv("/output/customers_clean.csv")