import functools
import psutil 

from fastapi import FastAPI, HTTPException, Query
from prometheus_client import Counter, Histogram, Gauge, generate_latest
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

CPU_USAGE = Gauge(
    "api_cpu_usage_percent",
    "CPU usage percent"
)

MEMORY_USAGE = Gauge(
    "api_memory_usage_percent",
    "Memory usage percent"
)

ERROR_RATE = Gauge(
    "api_error_rate",
    "API error rate (errors/requests)"
)

def track_metrics(endpoint_name):
    def decorator(func):
        @functools.wraps(func)  
        async def wrapper(*args, **kwargs):
            REQUEST_COUNT.labels(method="GET", endpoint=endpoint_name).inc()
            with REQUEST_LATENCY.labels(endpoint=endpoint_name).time():
                try:
                    result = await func(*args, **kwargs)
                except Exception:
                    ERROR_COUNT.labels(endpoint=endpoint_name).inc()
                    raise
            CPU_USAGE.set(psutil.cpu_percent())
            MEMORY_USAGE.set(psutil.virtual_memory().percent)
            total_requests = sum([REQUEST_COUNT.labels(method="GET", endpoint=ep)._value.get() for ep in ["add", "sub", "mul", "div"]])
            total_errors = sum([ERROR_COUNT.labels(endpoint=ep)._value.get() for ep in ["add", "sub", "mul", "div"]])
            if total_requests > 0:
                ERROR_RATE.set(total_errors / total_requests)
            else:
                ERROR_RATE.set(0)
            return result
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
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.virtual_memory().percent)
    return Response(generate_latest(), media_type="text/plain")