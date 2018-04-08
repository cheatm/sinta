from pymongo import UpdateOne, InsertOne
from collections import Iterable
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


def catch(data):
    data = data.sort_index()
    index = data.index
    today = index[0].date()
    start = 0
    end = 0
    for value in index:
        if value.date() == today:
            end += 1
        else:
            yield datetime(*today.timetuple()[:3]), data.iloc[slice(start, end)]
            start = end
            end += 1
            today = value.date()
    yield datetime(*today.timetuple()[:3]), data.iloc[slice(start, end)]


def make_docs(data):
    for date, daily in catch(data):
        dct = daily.to_dict("list")
        dct[data.index.name] = list(daily.index)
        dct["_d"] = date
        dct["_l"] = len(daily)
        yield dct


def insert_chunk_1min(collection, data):
    inserts = list(map(InsertOne, make_docs(data)))
    return collection.bulk_write(inserts).inserted_count


def update_chunk_1min(collection, data, upsert=True):
    return collection.bulk_write(list(make_update(data, upsert))).upserted_count


def make_update(data, upsert=True):
    for dct in make_docs(data):
        yield UpdateOne({'_d': dct["_d"]}, {"$set": dct}, upsert)


def chunk_length(col, date):
    return col.find_one({"_d": datetime.strptime(date, "%Y-%m-%d"), "_l": {"$exists": True}}, {"_l": 1, "_d": 1, "_id": 0})["_l"]


def read_chunk(collection, *dates):
    filters = {"_d": {"$in": [datetime.strptime(date, "%Y-%m-%d") for date in dates]}}
    return pd.DataFrame(get_docs(collection, filters)).set_index("datetime")


def get_docs(collection, filters=None, projection=None):
    dct = {}
    if isinstance(projection, dict):
        projection['_id'] = 0
        projection["_l"] = 1
    elif isinstance(projection, Iterable):
        projection = dict.fromkeys(projection, 1)
        projection["_id"] = 0
        projection["_l"] = 1
    else:
        projection = {"_id": 0}
    cursor = collection.find(filters, projection)
    for doc in cursor:
        l = doc.pop('_l')
        for key, values in doc.items():
            if isinstance(values, list) and (len(values) == l):
                dct.setdefault(key, []).extend(values)

    return dct

