import functools
import logging
toggle_decorators = False
logpath = './LogDetails/Logs.txt'
 
#Creates a logging object and returns it 
def create_logger():
    """Creates a logging object and returns it."""
    logger = logging.getLogger("example_logger")
    logger.setLevel(logging.INFO)
 
    # create the logging file handler
    fh = logging.FileHandler(logpath)
 
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)
 
    # add handler to logger object
    logger.addHandler(fh)
    return logger
 
def exception(function):
    """Logs errors from functions.

    A decorator that wraps the passed in function and logs 
    exceptions should one occur.
    """
    if not toggle_decorators:
        return function
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        logger = create_logger()
        try:
            return function(*args, **kwargs)
        except:
            # log the exception
            err = 'Function name: '
            err += function.__name__
            
            logger.exception(err)
 
            # re-raise the exception
            raise
    return wrapper