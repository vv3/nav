#!/usr/bin/python
"""
$Id: pinger.py,v 1.4 2002/08/26 20:55:02 magnun Exp $
$Source: /usr/local/cvs/navbak/navme/services/pinger.py,v $

"""
import os
os.sys.path.append(os.path.split(os.path.realpath(os.sys.argv[0]))[0]+"/lib")
os.sys.path.append(os.path.split(os.path.realpath(os.sys.argv[0]))[0]+"/lib/handler")
os.sys.path.append(os.path.split(os.path.realpath(os.sys.argv[0]))[0]+"/lib/ping")

import megaping, db, debug, config, signal, getopt, time, pwd

class pinger:
    def __init__(self, **kwargs):
        signal.signal(signal.SIGHUP, self.signalhandler)
        signal.signal(signal.SIGUSR1, self.signalhandler)
        signal.signal(signal.SIGTERM, self.signalhandler)
        self.config=config.pingconf()
        self.debug=debug.debug(level=int(self.config.get('debuglevel',5)))
        self.debug.log("Setting debuglevel=%s "% self.config.get('debuglevel',5))
        self._isrunning=1
        self._looptime=int(self.config.get('checkinterval',60))
        self.debug.log("Setting checkinterval=%i" %self._looptime)
        self._debuglevel=0
        self._pidfile=self.config.get('pidfile', 'pinger.pid')
        self.dbconf=config.dbconf()
        self.db=db.db(self.dbconf)
        self.down=[]
        sock = kwargs.get('socket',None)
        self.pinger=megaping.MegaPing(sock)
                      
    def getJobs(self):
        """
        Fetches new jobs from the NAV database and appends them to
        the runqueue.
        """

        hosts = self.db.hostsToPing()
        self.hosts = map(lambda x:x[0], hosts)

    def main(self):
        """
        Loops until SIGTERM is caught. The looptime is defined
        by self._looptime
        """

        while self._isrunning:
            start=time.time()
            self.getJobs()
            self.pinger.setHosts(self.hosts)
            elapsedtime=self.pinger.start()
            down = self.pinger.noAnswers()
            reportdown = filter(lambda x: x not in self.down, down)
            reportup = filter(lambda x: x not in down, self.down)
            self.down = down

            #Rapporter bokser som har g�tt ned
            for each in reportdown:
                self.db.pingEvent(each, 'DOWN')
                self.debug.log("%s marked as down." % each)
            #Rapporter bokser som har kommet opp
            for each in reportup:
                self.db.pingEvent(each, 'UP')
                self.debug.log( "%s marked as up." % each)

            self.debug.log("%i hosts checked in %03.3f secs. %i hosts currently marked as down." % (len(self.hosts),elapsedtime,len(self.down)))
            wait=self._looptime-elapsedtime
            self.debug.log("Sleeping %03.3f secs" % wait,6)
            time.sleep(wait)

    def signalhandler(self, signum, frame):
        if signum == signal.SIGTERM:
            self.debug.log("Caught SIGTERM. Exiting.",1)
            os.sys.exit(0)
        else:
            self.debug.log( "Caught %s. Resuming operation." % (signum),2)




def help():
    print """Paralell pinger for NAV (Network Administration Visualized).

    Usage: %s [OPTIONS]
    -h  --help      Displays this message
    -n  --nofork    Run in foreground
    -v  --version   Display version and exit

    Written by Stian S�iland and Magnus Nordseth, 2002
    """  % os.path.basename(os.sys.argv[0])

def start(nofork):
    """
    Forks a new prosess, letting the service run as
    a daemon.
    """
    conf = config.pingconf()
    if not nofork:
        pid=os.fork()
        if pid > 0:
            pidfile=conf.get('pidfile', 'pinger.pid')
            try:
                pidfile=open(pidfile, 'w')
                pidfile.write(str(pid)+'\n')
                pidfile.close()
            except Exception, e:
                print "Could not open %s" % pidfile
                print str(e)
            os.sys.exit()

        logfile = conf.get('logfile','pinger.log')
        print "Logger til ", logfile
        os.sys.stdout = open(logfile,'w')
        os.sys.stderr = open(logfile,'w')
    myPinger=pinger(socket=sock)
    myPinger.main()


def setUser():
    conf = config.pingconf()
    username = conf.get('user', 'nobody')
    try:
        uid = pwd.getpwnam(username)[2]
        gid = pwd.getpwnam(username)[3]
    except KeyError:
        print "User %s not found" % username
        print "Exiting"
        os.sys.exit()
    print "Setting UID to %s " % uid 
    os.setegid(gid)
    os.seteuid(uid)
    print "Now running as user %s" % username

if __name__=='__main__':
    try:
        opts, args = getopt.getopt(os.sys.argv[1:], 'hnv', ['help','nofork', 'version'])
        nofork=0

        for opt, val in opts:
            if opt in ('-h','--help'):
                help()
                os.sys.exit()
            elif opt in ('-n','--nofork'):
                nofork=1
            elif opt in ('-v','--version'):
                print __version__
                os.sys.exit(0)
                

    except (getopt.error):
        help()
        os.sys.exit(2)

    print "Creating socket"
    sock = megaping.makeSocket()
    setUser()
    start(nofork)
