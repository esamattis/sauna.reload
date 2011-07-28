
import time
from sauna.reload import forkloop

def startForkLoop(event):

    print "We saved at least %s seconds from boot up time" % (time.time() - forkloop.boot_started)
    forkloop.start()

