# -*- coding: utf-8 -*-
#
# Copyright (C) 2008, 2009 UNINETT AS
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.  You should have received a copy of the GNU General Public
# License along with NAV. If not, see <http://www.gnu.org/licenses/>.
#
"""ipdevpoll daemon.

This is the daemon program that runs the IP device poller.

"""

import sys
import logging, logging.config
from optparse import OptionParser

from twisted.internet import reactor

from nav import buildconf

from schedule import Scheduler
from plugins import import_plugins

def run_poller():
    """Load plugins, and initiate polling schedules."""
    global scheduler
    import_plugins()
    scheduler = Scheduler()
    return scheduler.run()

def get_parser():
    """Setup and return a command line option parser."""
    parser = OptionParser(version="NAV " + buildconf.VERSION)
    parser.add_option("-c", "--config", dest="configfile",
                      help="read configuration from FILE", metavar="FILE")
    parser.add_option("-l", "--logconfig", dest="logconfigfile",
                      help="read logging configuration from FILE",
                      metavar="FILE")
    return parser


def main():
    """Main execution function"""
    parser = get_parser()
    (options, args) = parser.parse_args()

    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('ipdevpoll')
    logger.info("--- Starting ipdevpolld ---")

    reactor.callWhenRunning(run_poller)
    reactor.run()

if __name__ == '__main__':
    main()
