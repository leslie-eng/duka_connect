## API DATA EXTRACTION

### Description

This is a script that fetches data from a REST API reliably, transforms the data and exports a CSV file.

The fetching step is built to fail loudly. `fetch_users` sets a timeout on every request and raises a specific error for each way a call can go wrong: a connection failure, a timeout, a status code other than 200, or a response body that is not valid JSON. Because of this, a failed request stops with a clear message instead of passing `None` to the next stage and surfacing later as a confusing `TypeError`.

The transformation step deals with the fact that each user record is nested. An address contains a `geo` object, which in turn holds `lat` and `lng`, and a company holds its own `name`. Before any cleaning, `describe_structure` prints the Python type of the payload, of one record and of every nested value, which makes the real shape of the data visible instead of assumed. `flatten_user` then turns each record into a single-level dict, so that `address -> geo -> lat` becomes the key `address_geo_lat`. Fields that are missing from a record are filled with NaN, so every row ends up with the same columns.

Both `flatten_user` and the helper inside `describe_structure` are written recursively. The depth of the nesting is not known in advance, and a nested dict follows the same rules as the record that contains it, so one function can handle every level: if a value is a dict, the function calls itself on it and carries the key path along, and anything else is stored as it is. Nested loops would only cover a fixed number of levels and would miss data if the API added another one. A library call such as `pandas.json_normalize` gives the same flattening in one line, but writing it by hand keeps the logic visible and avoids a dependency for a small job.

The final step writes the flattened records to a CSV file with one row per user.

### Installation

```
pip install -r requirements.txt
```

The script uses type hints such as `list[dict]`, so it needs Python 3.9 or later. The `requests` library handles the HTTP calls.

### Usage

Run the script from the project folder:

```
python main.py
```

On a successful run it fetches the users from the API, prints the structure of the payload, flattens every record and saves the result as `users.csv` in the same folder. If the API is unreachable, times out, returns an error status or sends something that is not JSON, the script stops and reports which of these happened.

### Roadmap

The flattening currently leaves lists as they are, so a field that holds a list of dicts is stored as a single value. Expanding those into indexed keys such as `tags_0` is the next change. Two other gaps are worth closing: flattened keys can collide if a record has both `address_city` and a nested `address -> city`, and the fetch step does not retry on temporary failures such as a 429 or a 5xx response. Adding a limited retry with a short wait would make the "reliable" part of the description stronger, and replacing the `print` calls with the `logging` module would make the output easier to control.

### Authors and acknowledgement

Written by Leslie.

### License

No license has been chosen for this project yet.

### Project status

In development. The fetching, flattening and CSV export work end to end, and the items in the roadmap are still to be done.