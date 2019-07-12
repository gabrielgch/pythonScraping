import time
import functools
import logging
import datetime
import os
import functools
import project_globals

def log(ans, filepath):
    """Writes to file log."""
    f = open(filepath, "a")
    f.write(ans + "\n")
    f.close()
 
def time_it(fn):
    """Decorator to measure run time of a method."""
    def inner(*args, **kwargs):
        if project_globals.toggle_timer:
            start = time.time()
            rs = fn(*args,**kwargs)
            end = time.time()
            ans = "Function {0} took {1}s".format(fn.__name__, end-start)
            print(ans)
            if project_globals.log_time:
                log(ans, project_globals.time_logfile)
            return rs
        else:
            return fn(*args, **kwargs)
    return inner

def log_calls(fn):
    """Logs calls to webapp."""
    @functools.wraps(fn)
    def inn(*args, **kwargs):
        if project_globals.toggle_log:
            today_time = datetime.datetime.now()
            res = fn(*args,**kwargs)
            ans = "Function {0} was called on {1}".format(
                fn.__name__, today_time)
            print(ans)
            if project_globals.do_log:
                log(ans, project_globals.logpath)
            return res 
        else:
            return fn(*args, **kwargs)
    return inn
