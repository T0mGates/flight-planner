import sentry_sdk

def init_fast_api_sentry()-> None:
    """
    Init sentry sdk for integration with FastAPI
    
    Logs usage:
        sentry_sdk.logger.info('This is an info log message')
        sentry_sdk.logger.warning('This is a warning message')
        sentry_sdk.logger.error('This is an error message')
        
    Python's default logger from the logging module will also be automatically
    forwarded to Sentry
    
    """
    sentry_sdk.init(
        dsn="https://cbcfcfd3a9725650f55d2c014be7a3bd@o4510726117982208.ingest.us.sentry.io/4510726150488064",
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
        # Enable sending logs to Sentry
        enable_logs=True
    )