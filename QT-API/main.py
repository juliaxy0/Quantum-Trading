from fastapi import FastAPI
from sentiment import sentimentAnalysisClass
from prediction import PredictionClass
import threading
import time

# MongoDB
from dotenv import dotenv_values
from pymongo import MongoClient
from app.routers.user import user
from app.routers.robot import robot
from app.routers.transaction import transaction

####################### Sentiment API

sentiment = FastAPI(title="Quantum Trading Sentiment Analysis API")

# Sentiment Analysis for each crypto
@sentiment.on_event("startup")
def startup_event():
    # Start the continuous task in a separate thread on application startup
    continuous_thread = threading.Thread(target=all_crypto_sa, daemon=True)
    continuous_thread.start()

# Endpoints
@sentiment.get('/')
async def root():
        return {'text':'Welcome to QuantumTrading Sentiment Analysis API'}

def all_crypto_sa():

    try:

        btc = sentimentAnalysisClass("BTC")
        eth = sentimentAnalysisClass("ETH")
        link = sentimentAnalysisClass("LINK")
        ltc = sentimentAnalysisClass("LTC")

        while True:
            btc.analyse()
            print("Updated BTC sentiment analysis")
            eth.analyse()
            print("Updated ETH sentiment analysis")
            link.analyse()
            print("Updated LINK sentiment analysis")
            ltc.analyse()
            print("Updated LTC sentiment analysis")

            time.sleep(5)

    except Exception as e:
        # Print or log the exception details
        print(f"Exception: {e}")
        return {"error": f"Internal server error: {e}"}  
################################ Prediction API

predict = FastAPI(title="Quantum Trading Prediction API")

# Sentiment Analysis for each crypto
@predict.on_event("startup")
def startup_event():
    print("started")
    # Start the continuous task in a separate thread on application startup
    continuous_thread = threading.Thread(target=all_crypto_predict, daemon=True)
    continuous_thread.start()

# Endpoints
@predict.get('/')
async def root():
        return {'text':'Welcome to QuantumTrading Prediction API'}

def all_crypto_predict():

    try: 
        btc = PredictionClass("btc")
        eth = PredictionClass("eth")
        link = PredictionClass("link")
        ltc = PredictionClass("ltc")
    

        while True:
            btc.update_csv()
            print("Updated BTC prediction")
            eth.update_csv()
            print("Updated ETH prediction")
            link.update_csv()
            print("Updated LINK prediction")
            ltc.update_csv()
            print("Updated LTC prediction")
            time.sleep(60)

    except Exception as e:
        # Print or log the exception details
        print(f"Exception: {e}")
        return {"error": f"Internal server error: {e}"}
    
################################ Database API

config = dotenv_values(".env")

database = FastAPI(title="Quantum Trading Database API")

@database.on_event("startup")
def startup_db_client():
    database.mongodb_client = MongoClient(config["ATLAS_URI"])
    database.database = database.mongodb_client[config["DB_NAME"]]
    print("Connected to the MongoDB database!")

@database.on_event("shutdown")
def shutdown_db_client():
    database.mongodb_client.close()

@database.get('/')  
async def root(): 
        return {'text':'Welcome to QuantumTrading Database API'} 
 
database.include_router(user, tags=["user"], prefix="/user") 
database.include_router(robot, tags=["robot"], prefix="/user/{id}/robot")
database.include_router(transaction, tags=["transaction"], prefix="/user/{id}/robot/{robotName}/transaction")