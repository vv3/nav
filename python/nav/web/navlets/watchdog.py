#
# Copyright (C) 2014 UNINETT AS
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
"""Module comment"""

from . import Navlet
from nav.watchdog.util import get_statuses


class WatchDogWidget(Navlet):
    """Widget for displaying WatchDog status"""

    title = 'WatchDog'
    description = 'Displays important statuses for NAV'

    def get_context_data(self, **kwargs):
        context = super(WatchDogWidget, self).get_context_data(**kwargs)
        context['tests'] = get_statuses()
        return context

    def get_template_basename(self):
        return 'watchdog'


