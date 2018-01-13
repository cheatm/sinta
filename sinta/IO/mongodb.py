from pymongo import UpdateOne, InsertOne
from datetime import datetime
import pandas as pd


def time_range(date):
    dt = datetime.strptime(date, "%Y-%m-%d")
    start = dt.replace(hour=9, minute=30)
    end = dt.replace(hour=15)
    return {"datetime": {"$gt": start, "$lte": end}}


def read(collection, *dates):
    f = {'$or': [time_range(date) for date in dates]}
    data = pd.DataFrame(list(collection.find(f, {"_id": 0})))
    return data.set_index("datetime")


def insert(collection, frame, index="datetime"):
    frame[index] = frame.index
    docs = [InsertOne(row.to_dict()) for time, row in frame.iterrows()]
    return collection.bulk_write(docs).inserted_count


def update(collection, frame, index='datetime'):
    frame[index] = frame.index
    docs = [UpdateOne({index: time}, {"$set": row.to_dict()}, upsert=True) for time, row in frame.iterrows()]
    return collection.bulk_write(docs).upserted_count


def length(collection, date):
    return collection.find(time_range(date)).count()
