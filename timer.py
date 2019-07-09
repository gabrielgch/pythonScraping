import time
import functools
import logging
 
#Creates a logging object
def create_logger():
    """
    Creates a logging object and returns it
    """
    logger = logging.getLogger("Time Logger")
    logger.setLevel(logging.INFO)
 
    # create the logging file handler
    fh = logging.FileHandler("./LogDetails/RunTime.txt")
 
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)
 
    # add handler to logger object
    logger.addHandler(fh)
    return logger

#Decorator function to declare the run time of a method
def timeit(method):
    
    def timed(*args, **kw):
        logger = create_logger()
       
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
                name = kw.get(
            'log_name', method.__name__.upper())
                kw[
            'log_time'][name] = int((te - ts) * 1000)
        else:   
            logger.exception('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
        return result
    return timed
