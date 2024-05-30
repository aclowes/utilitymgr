import datetime
import json

from google.cloud import storage

client = storage.Client(project="wise-vim-178017")
bucket = client.bucket('static.yawn.live')

read_dates = [
    ("12/27/22", 0),
    ("01/27/23", 166.978),
    ("02/21/23", 108.310),
    ("03/28/23", 113.743),
    ("04/18/23", 206.938),
]
read_dates = [
    (datetime.datetime.strptime(date, "%m/%d/%y").date(), read)
    for date, read in read_dates
]
thermostats = "cc-c0-79-02-af-a1 cc-c0-79-00-ed-0b b8-d7-af-43-7b-b7".split()
date = read_dates.pop(0)[0]
bills = []
bill_hours = 0

while True:
    date += datetime.timedelta(days=1)
    hours = 0
    for thermostat in thermostats:
        for x in range(7):
            file_date = date + datetime.timedelta(days=x)
            file_name = f'utilitymgr/archive/{file_date}_data/lux_{thermostat}.json'
            blob = bucket.get_blob(file_name)
            if blob:
                break
        body = json.loads(blob.download_as_text())
        t = datetime.datetime.strptime(body['dailyruntime'][x]['totalruntime'], "%H:%M:%S")
        hours += t.hour + t.minute / 60 + t.second / 3600

    print(f"{date} {hours:.1f} hours")
    bill_hours += hours

    if date == read_dates[0][0]:
        bills.append(f"{date}: {bill_hours:d} hours {read_dates[0][1]} gallons")
        read_dates.pop(0)
        bill_hours = 0
        if not read_dates:
            break

for line in bills:
    print(line)

"""
2023-01-27: 169.6 hours 166.978 gallons
2023-02-21: 107.8 hours 108.31 gallons
2023-03-28: 202.4 hours 113.743 gallons
2023-04-18: 89.6 hours 206.938 gallons
"""