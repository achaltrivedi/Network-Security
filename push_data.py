import os
import sys
import json

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL=os.getenv("MONGO_DB_URL")
print(MONGO_DB_URL)

import certifi
ca=certifi.where()

import pandas as pd
import numpy as np
import pymongo
from pymongo import MongoClient
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

class NetworkDataExtract():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def csv_to_json_convertor(self,file_path):
        try:
            data=pd.read_csv(file_path)
            data.reset_index(drop=True,inplace=True)
            records = data.to_dict(orient="records")
            return records
        except Exception as e:
            print(f"[ERROR] While inserting to MongoDB: {e}")
            raise NetworkSecurityException(e,sys)
   
    def insert_data_mongodb(self,records,DATABASE,Collection):
        try:
            client = MongoClient(MONGO_DB_URL, tls=True, tlsCAFile=certifi.where())
            db = client["AchalDB"]
            collection = db["NetworkData"]
            result = collection.insert_many(records)
            no_of_records = len(result.inserted_ids)
            return no_of_records
        except Exception as e:
            print(f"[ERROR] While inserting to MongoDB: {e}")
            raise NetworkSecurityException(e,sys)

        
if __name__=='__main__':
    FILE_PATH="Network_Data\phisingData.csv"
    DATABASE="AchalDB"
    Collection="NetworkData"
    networkobj=NetworkDataExtract()
    records=networkobj.csv_to_json_convertor(file_path=FILE_PATH)
    print(records)
    no_of_records=networkobj.insert_data_mongodb(records,DATABASE,Collection)
    print(no_of_records)
        


