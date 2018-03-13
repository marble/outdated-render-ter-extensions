# mb, 2012-05-24, 2012-05-24

# 2012-05-24: allow dt=<str>

import sys
from datetime import datetime

class Logger:

    def __init__(self, fname=None):
        self.fname = fname
        self.cnt = 0
        self.f2 = None
        if self.fname is None:
            self.f2 = sys.stdout
        else:
            self.f2 = file(self.fname, 'w')

    def close(self):
        if self.f2 and self.f2 != sys.stdout:
            self.f2.close()

    def stream(self):
        return self.f2

    def msg(self, msg=None, nl=None, cnt=False, dt=True):
        if dt:
            if type(dt) == str:
                n = 19 - len(dt)
                if n > 0:
                    self.f2.write('                    '[:n])
                self.f2.write('%s ' % dt[:19])
            else:
                self.f2.write('%s ' % (str(datetime.now())[:19]))
        if cnt:
            self.cnt += 1
            self.f2.write('[%s] ' % self.cnt)
        if (msg):
            self.f2.write(msg)
        if (nl):
            self.f2.write(nl)

if __name__=="__main__":
    NL = '\n'
    log = Logger()
    for i in range(1,4):
        log.msg('message %s' % i, NL)
    for i in range(4,7):
        log.msg('message %s' % i, NL, dt=False)
    for i in range(7,10):
        log.msg('message %s' % i, NL, dt=False, cnt=True)
    for i in range(10,13):
        log.msg('message %s' % i, NL, dt=True, cnt=True)
    import subprocess
    try:
        subprocess.call('ls', stdout=log.stream(), shell=True)
    except AttributeError:
        pass
    
