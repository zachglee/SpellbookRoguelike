import uvicorn

if __name__ == "__main__":
    config = uvicorn.Config(
        "server:app",
        port=8000,
        host="127.0.0.1",
        log_level="debug",
        reload=True)
    server = uvicorn.Server(config)
    server.run()
