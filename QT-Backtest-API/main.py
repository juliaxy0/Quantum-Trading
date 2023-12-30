from fastapi import FastAPI, HTTPException
from backtest import backtestClass
from fastapi.responses import JSONResponse

app = FastAPI(title="Quantum Trading Backtesting API")

# Endpoints
@app.get('/')
async def root():
        return {'text':'Welcome to QuantumTrading Backtesting API'}

# Return crypto analysis result
@app.get("/backtest/{stratergy}")
async def backtesting(stratergy: str):
    result = backtestClass.start_backtest(stratergy)
    return result
    
