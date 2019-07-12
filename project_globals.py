import os

DEFAULT_PATH = os.path.join(os.getcwd(), os.path.basename('/LogDetails'))
DEFAULT_CALLLOG_FILENAME = 'Logs.txt'
DEFAULT_TIMELOG_FILENAME = 'RunTime.txt'
toggle_timer = False
log_time = False
time_logfile = os.path.join(DEFAULT_PATH,DEFAULT_TIMELOG_FILENAME)
toggle_log=False
do_log=False
logpath = os.path.join(DEFAULT_PATH,DEFAULT_CALLLOG_FILENAME)