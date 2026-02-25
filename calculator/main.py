import functools

from fastapi import FastAPI, HTTPException, Query
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response

app = FastAPI(title="Calculator API")

REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total number of API requests",
    ["method", "endpoint"]
)

REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds",
    "Request latency",
    ["endpoint"]
)

ERROR_COUNT = Counter(
    "api_errors_total",
    "Total number of errors",
    ["endpoint"]
)

def track_metrics(endpoint_name):
    def decorator(func):
        @functools.wraps(func)  
        async def wrapper(*args, **kwargs):
            REQUEST_COUNT.labels(method="GET", endpoint=endpoint_name).inc()
            with REQUEST_LATENCY.labels(endpoint=endpoint_name).time():
                try:
                    return await func(*args, **kwargs)
                except Exception:
                    ERROR_COUNT.labels(endpoint=endpoint_name).inc()
                    raise
        return wrapper
    return decorator

@app.get("/add")
@track_metrics("add")
async def add(a: float = Query(...), b: float = Query(...)):
    return {"operation": "add", "result": a + b}

@app.get("/sub")
@track_metrics("sub")
async def sub(a: float = Query(...), b: float = Query(...)):
    return {"operation": "sub", "result": a - b}

@app.get("/mul")
@track_metrics("mul")
async def mul(a: float = Query(...), b: float = Query(...)):
    return {"operation": "mul", "result": a * b}

@app.get("/div")
@track_metrics("div")
async def div(a: float = Query(...), b: float = Query(...)):
    if b == 0:
        ERROR_COUNT.labels(endpoint="div").inc()
        raise HTTPException(status_code=400, detail="Division by zero")
    return {"operation": "div", "result": a / b}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")