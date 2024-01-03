from fastapi import FastAPI, HTTPException
from prediction import PredictionClass
import threading
import time

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
        