#!/bin/bash
#
# Copyright (c) 2015 ThoughtWorks, Inc.
#
# Pixelated is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pixelated is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Pixelated. If not, see <http://www.gnu.org/licenses/>.

for user in `seq $1`; do
	echo "Sending $2 mails for user loadtest$user"
	for email in `seq $2`; do
	    sendemail -f loadtest${user}@dev.pixelated-Project.org -t loadtest${user}@dev.pixelated-project.org -u Hello$email -m Ha$email
	done
done
