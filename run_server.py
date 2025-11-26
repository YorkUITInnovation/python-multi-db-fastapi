import uvicorn

if __name__ == "__main__":
    # Always bind to port 8082
    uvicorn.run("app.main:app", host="0.0.0.0", port=8082, reload=True, log_level="info")

