from fastapi import FastAPI, HTTPException
from sentiment import sentimentAnalysisClass
import threading
import time
import pandas as pd
import os

app = FastAPI(title="Quantum Trading Sentiment Analysis API")

# Sentiment Analysis for each crypto
@app.on_event("startup")
def startup_event():
    # Start the continuous task in a separate thread on application startup
    continuous_thread = threading.Thread(target=all_crypto_sa, daemon=True)
    continuous_thread.start()

    # continuous_thread1 = threading.Thread(target=BTC_SA, daemon=True)
    # continuous_thread1.start()

    # continuous_thread2 = threading.Thread(target=ETH_SA, daemon=True)
    # continuous_thread2.start()

    # continuous_thread3 = threading.Thread(target=LINK_SA, daemon=True)
    # continuous_thread3.start()

    # continuous_thread4 = threading.Thread(target=LTC_SA, daemon=True)
    # continuous_thread4.start() 

# Endpoints
@app.get('/')
async def root():
        return {'text':'Welcome to QuantumTrading Sentiment Analysis API'}

# Return crypto analysis result
@app.get("/check_sentiment/{crypto}")
async def read_item(crypto: str):
    result = check_sentiment(crypto)
    return result

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
        
def check_sentiment(crypto: str) -> dict:
    try:
        # Check if the file exists
        file_path = '{}.csv'.format(crypto)
        if not os.path.isfile(file_path):
            print("Error {}: File does not exist.".format(crypto))

        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)

        # Check if the DataFrame has at least 10 rows
        if len(df) < 10:
            print("Error {}: Not enough rows in the DataFrame.".format(crypto))

        # Extract the 'Sentiment' column from the last 20 rows
        last_10_sentiments = df.tail(10)['Sentiment']

        # Check if at least 10 out of the last 20 rows have a positive sentiment
        positive_sentiments = last_10_sentiments[last_10_sentiments == 'POSITIVE']
        if len(positive_sentiments) >= 5:
            return {"positive_count": len(positive_sentiments), "result": True}
        else:
            return {"positive_count": len(positive_sentiments), "result": False}

    except Exception as e:
        # Print or log the exception details
        print(f"Exception: {e}")
    
# # BTC Sentiment
# def BTC_SA():
#     while True:
#         crypto = "BTC"
#         try:
#             a = sentimentAnalysisClass(crypto)
#             a.analyse()
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=str(e))
        
#         time.sleep(10)  # Sleep for 10 seconds before repeating
    
# # ETH Sentiment
# def ETH_SA():
#     while True:
#         crypto = "ETH"
#         try:
#             b = sentimentAnalysisClass(crypto)
#             b.analyse()
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=str(e))
        
#         time.sleep(10)  # Sleep for 10 seconds before repeating
    
# # LINK Sentiment
# def LINK_SA():
#     while True:
#         crypto = "LINK"
#         try:
#             c = sentimentAnalysisClass(crypto)
#             c.analyse()
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=str(e))
        
#         time.sleep(10)  # Sleep for 10 seconds before repeating
    
# # LTC Sentiment
# def LTC_SA():
#     while True:
#         crypto = "LTC"
#         try:
#             d = sentimentAnalysisClass(crypto)
#             e.analyse()
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=str(e))
        
#         time.sleep(10)  # Sleep for 10 seconds before repeatingz
    
