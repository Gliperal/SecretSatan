from datetime import datetime

LOGFILE='log.txt'

def log(message):
    timestamp = datetime.now()
    with open(LOGFILE, 'a') as f:
        f.write(f'[{timestamp}] {message}\n')

