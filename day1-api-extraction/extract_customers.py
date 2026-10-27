"""
Day 1 - API Data Extraction and Transformation
Squad Python Specialization - Data Engineering

Fill in every function. Keep the signatures; you may add helpers of your own.
"""
import csv
import json
from pathlib import Path

import pandas as pd
import requests


API_URL = "https://jsonplaceholder.typicode.com/users"
OUTPUT_PATH = Path("output") / "customers_clean.csv"


def fetch_users(url: str = API_URL, timeout: float = 10.0) -> list[dict]:
    """Retrieve the list of users from the API.

    Must raise or report a clear error for: connection failures, timeouts,
    non-200 status codes and bodies that are not valid JSON.
    """
    try:
        response = requests.get(url=url, timeout=timeout)
    
    # handle timeouts
    except requests.exceptions.Timeout as e:
        raise TimeoutError(f"Request timed out after {timeout}s") from e
    
    # handle connection failures   
    except requests.exceptions.ConnectionError:
        print(f"Could not connect to API: {url}")
        
    # handle the non-200 error codes
    if response.status_code != 200:
                raise RuntimeError(f" The API returned status {response.status_code}")
        
    # check if the data is json 
    try:
        data = response.json()
    
     # handling non json body
    except ValueError as e:
            raise ValueError(f"Expected JSON but got: {response.text}") from e
        
    # check if data is of type list
    
    if not isinstance(data, list):
        raise ValueError(f"Expected a list of users, got {type(data).__name__}")
        
    return data
    


def describe_structure(payload) -> None:
    """Print what Python types the payload and one record are made of
    (the top-level container, a record, and each nested value)."""
    
    # this is a recursive function that checks if we have nested 
    # values within a list/ dict and prints out the data type
    def describe_value(name, value, indent:int) -> None:
        padding = " " * indent
        print(f"{padding}{name}: {type(value).__name__}", indent)
        
        if isinstance(value, dict):
            for k, v in value.items():
                describe_value(k, v, indent + 1)
        elif isinstance(value, list) and value:
            describe_value("[0]", value[0], indent + 1)
            
    print(f"Payload : {type(payload).__name__}")
    
    if not isinstance(payload, list) or not payload:
        print("Payload is empty or not a list")
        return
    
    record = payload[0]
    print(f"Record: {type(record).__name__}")
    
    
    if isinstance(record, dict):
        for key, value in record.items():
            describe_value(key, value, indent=1)
        
    

def extract_core_fields(users: list[dict]) -> list[dict]:
    """Return one small dict per user with id, name, email, city and company name."""
    # rule:  a missing nested key returns NaN
    # setup an empty list that will hold the data
    nan = float("nan")
    
    data = []
    user_data = dict
    for user in users:
        user_data = {
            'id': user.get('id', nan),
            'name': user.get('name',nan),
            'email': user.get('email',nan),
            'city' : user.get('address',nan).get('city', {}),
            'company name': user.get('company', nan).get('name', {})
        }
        data.append(user_data)

    return data
    


def build_structures(users: list[dict]) -> tuple[list, list[tuple], dict]:
    """Return (list_of_names, list_of_(id, email)_tuples, dict_of_id_to_city).

    Use at least one list comprehension and one dict comprehension.
    """
    if not isinstance(users, list):
        raise TypeError(f"The data is of type {type(users).__name__}")
    
        
    # get a list of names
    names = [user.get('name') for user in users]
    
    id_email = []
    
    nan = float("nan")
    
    for user in users:
        constant = (user.get('id'), user.get('email'))
        id_email.append(constant)
    
    dict_id_city = {
        user.get("id"): (user.get("address") or {}).get("city", nan) for user in users}
    
    
    return names, id_email, dict_id_city



def flatten_user(user: dict, parent_key: str = "", sep: str = "_") -> dict:
    """Flatten one nested user record into a single-level dict.

    e.g. a nested address -> geo -> lat becomes the key address_geo_lat.
    """
    flatten = {}
    for key, value in user.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key 
        if isinstance(value, dict):
            flatten.update(flatten_user(value, new_key, sep))
        else:
            flatten[new_key] = value
    return flatten
     

def to_dataframe(flat_users: list[dict]) -> pd.DataFrame:
    """Build a DataFrame with the columns in the expected-output order."""
    expected_columns = ["customer_id", "name", "username", "email", "phone", "website", "address_street", "address_suite",
                            "address_city", "address_zipcode", "address_geo_lat", "address_geo_lng", "company_name", "company_catchphrase"
                            "company_bs"
                            ]
    
    df = pd.DataFrame(flat_users)
    print(f"The shape of the dataframe {df.shape}")
    print(f"the dtypes of the dataframe {df.info()}")
    
    # check the id is updated as customer_id
    if "id" in df.columns:
        df = df.rename(columns={"id":"customer_id"})
    
    if "address_geo_lat" in df.columns:
        df["address_geo_lat"] = pd.to_numeric(df["address_geo_lat"], errors="coerce")
    
    if "address_geo_lng" in df.columns:
        df["address_geo_lng"] = pd.to_numeric(df["address_geo_lng"], errors="coerce")
    
    df = df[[column for column in expected_columns if column in df.columns]]
    
    return df


def export_csv(df: pd.DataFrame, path: Path = OUTPUT_PATH) -> Path:
    """Write the DataFrame to CSV (creating the folder if needed) and return the path."""
    # create a folder or check if the folder exists
    path.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(path_or_buf=path, index=False)
    return path


def main() -> None:
    # TODO: wire the steps together and print a short run summary.
    print("Starting API data extraction...")
   
    #Fetch data from API
    print(f"Fetching data from {API_URL}...")
    users = fetch_users()
    print(f"Fetched data successfully. Fetched {len(users)} records.")

    # Describe structure of extracted data
    describe_structure(users)

    # Extract core fields
    core_fields = extract_core_fields(users)
    print(f"{len(core_fields)} users extracted.")

    # Build structures
    names, tuples, city_dict = build_structures(users)
    print("-------Structuring Data Demo-----------")
    print(f"First 5 names: {names[:5]}")
    print(f"First 5 (id, email) tuples: {tuples[:5]}")
    print(f"ID -> City mapping: {list(city_dict.items())[:5]}")

    # Flatten all records
    flat_users = [flatten_user(user) for user in users]
    print(f"{len(flat_users)} records flattened.")

    # Load DataFrame and print df info
    df = to_dataframe(flat_users=flat_users)
    print("---------DataFrame info-------------")
    print(f"Shape: {df.shape}")
    print("Data Types", df.dtypes)

    # Export to CSV
    saved_data_path = export_csv(df)
    print(f"Cleaned data exported to: {saved_data_path}")
    
    
    

if __name__ == "__main__":
    main()
