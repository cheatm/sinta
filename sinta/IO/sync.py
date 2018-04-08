from pymongo import UpdateOne, InsertOne
import pandas as pd


def iter_insert(data):
    if isinstance(data, pd.DataFrame):
        for key, values in data.reset_index().iterrows():
            yield make_insert(values)


def make_insert(series):
    dct = series.dropna().to_dict()
    return InsertOne(dct)


def insert(collection, data):
    return collection.bulk_write(list(iter_insert(data))).inserted_count


def iter_update(data, **kwargs):
    if isinstance(data.index, pd.MultiIndex):
        names = data.index.names
        for key, values in data.reset_index().set_index(names, drop=False).iterrows():
            yield make_update(values, dict(zip(data.index.names, key)), **kwargs)
    else:
        for key, values in data.iterrows():
            yield make_update(values, {data.index.name: key}, **kwargs)


def make_update(series, filters, upsert=True, **kwargs):
    return UpdateOne(filters, {"$set": series.dropna().to_dict()}, upsert=upsert)


def update(collection, data, **kwargs):
    result = collection.bulk_write(list(iter_update(data, **kwargs)))
    return result.matched_count, result.upserted_count


