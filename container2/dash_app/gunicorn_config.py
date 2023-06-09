# Gunicorn configuration file.
# HiveKeepers - container2 - dash_app/gunicorn_config.py
# written by: Andrew McDonald
# initial: 28/01/22
# current: 19/03/22
# version: 0.9

from multiprocessing import cpu_count
from os import environ

def max_workers():    
    return cpu_count()

# Server socket
#
#   bind - The socket to bind.
#
#       A string of the form: 'HOST', 'HOST:PORT', 'unix:PATH'.
#       An IP is a valid HOST.

environ.get('APP_PORT', '8050')
bind = '0.0.0.0:' + environ.get('APP_PORT', '8050')

# Worker processes
#
#   workers - The number of worker processes that this server
#       should keep alive for handling requests.
#
#       A positive integer generally in the 2-4 x $(NUM_CORES)
#       range. You'll want to vary this a bit to find the best
#       for your particular application's work load.
#
#   worker_tmp_dir
#
#     A directory to use for the worker heartbeat temporary file.
#
#   threads
#
#       The number of worker threads for handling requests.

threads_default = max_workers() - 1
worker_tmp_dir = '/dev/shm'
workers = environ.get('APP_WORKERS', max_workers())
threads = environ.get('APP_THREADS', threads_default)

#
#   spew - Install a trace function that spews every line of Python
#       that is executed when running the server. This is the
#       nuclear option.
#
#       True or False
#

spew = False

#
# Server mechanics
#
#   pidfile - The path to a pid file to write
#
#       A path string or None to not write a pid file.
#

pidfile = '/var/run/gunicorn.pid'

#
#   Logging
#
#   logfile - The path to a log file to write to.
#
#       A path string. "-" means log to stdout.
#
#   loglevel - The granularity of log output
#
#       A string of "debug", "info", "warning", "error", "critical"
#

# set log locations
gunicorn_log = '/home/hivekeeper/persistent/logs/container2/gunicorn.log'
gunicorn_error_log = '/home/hivekeeper/persistent/logs/container2/gunicorn-error.log'
gunicorn_access_log = '/home/hivekeeper/persistent/logs/container2/gunicorn-access.log'

accesslog = gunicorn_access_log
errorlog = gunicorn_error_log
loglevel = environ.get('APP_LOG_LEVEL', 'info').lower()

#access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

#
# Process naming
#
#   proc_name - A base to use with setproctitle to change the way
#       that Gunicorn processes are reported in the system process
#       table. This affects things like 'ps' and 'top'. If you're
#       going to be running more than one instance of Gunicorn you'll
#       probably want to set a name to tell them apart. This requires
#       that you install the setproctitle module.
#
#       A string or None to choose a default of something like 'gunicorn'.
#

proc_name = 'hivekeeper_app'

#
# Server hooks
#
#   post_fork - Called just after a worker has been forked.
#
#       A callable that takes a server and worker instance
#       as arguments.
#
#   pre_fork - Called just prior to forking the worker subprocess.
#
#       A callable that accepts the same arguments as after_fork
#
#   pre_exec - Called just prior to forking off a secondary
#       master process during things like config reloading.
#
#       A callable that takes a server instance as the sole argument.
#

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    pass

def pre_exec(server):
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

    ## get traceback info
    import threading, sys, traceback
    id2name = {th.ident: th.name for th in threading.enumerate()}
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append("\n# Thread: %s(%d)" % (id2name.get(threadId,""),
            threadId))
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s' % (filename,
                lineno, name))
            if line:
                code.append("  %s" % (line.strip()))
    worker.log.debug("\n".join(code))

def worker_abort(worker):
    worker.log.info("worker received SIGABRT signal")