#############################################################################
# Copyright (c) Members of the EGEE Collaboration. 2006-2010.
# See http://www.eu-egee.org/partners/ for details on the copyright holders.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors:
#     Joel Casutt     - joel.casutt@switch.ch
#############################################################################

PROBES_NAMESPACE = nagios-plugins-argus
PROBES_LIBEXECDIR = /usr/libexec/grid-monitoring/probes/$(PROBES_NAMESPACE)
PROBES_VARDIR = /var/lib/grid-monitoring/$(PROBES_NAMESPACE)

all: install

install:
	@echo "Installing Nagios probes in $(DESTDIR)$(PROBES_LIBEXECDIR)..."
	@install -v -d $(DESTDIR)$(PROBES_LIBEXECDIR)
	@install -v -m 0750 src/nagios-plugins-argus.* $(DESTDIR)$(PROBES_LIBEXECDIR)
	@install -v -d $(DESTDIR)$(PROBES_LIBEXECDIR)/framework
	@install -v -m 0644 src/framework/*.py $(DESTDIR)$(PROBES_LIBEXECDIR)/framework
	@install -v -d $(DESTDIR)$(PROBES_VARDIR)
