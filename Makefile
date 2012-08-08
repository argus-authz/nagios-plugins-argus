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
#     Joel Casutt     <joel.casutt@switch.ch>
#     Valery Tschopp  <valery.tschopp@switch.ch>
#############################################################################

PROBES_NAMESPACE = nagios-plugins-argus
PROBES_LIBEXECDIR = /usr/libexec/grid-monitoring/probes/$(PROBES_NAMESPACE)
PROBES_VARDIR = /var/lib/grid-monitoring/$(PROBES_NAMESPACE)

name=nagios-plugins-argus
spec_file=fedora/$(name).spec
version=$(shell grep "Version:" $(spec_file) | sed -e "s/Version://g" -e "s/[ \t]*//g")
release=1
rpmbuild_dir=$(shell pwd)/rpmbuild
stage_dir=$(shell pwd)/stage


all: install

dist:
	@echo "Packaging sources"
	@rm -fr $(name)-$(version)
	@mkdir $(name)-$(version)
	@cp -rv src $(name)-$(version)
	@cp -v Makefile $(name)-$(version)
	@cp -v COPYRIGHT LICENSE README AUTHORS CHANGELOG $(name)-$(version)
	@rm -f $(name)-$(version).tar.gz
	@tar -cvzf $(name)-$(version).tar.gz $(name)-$(version)
	@rm -fr $(name)-$(version)

clean:
	@echo "Cleaning..."
	rm -fr $(name)-$(version) *.tar.gz rpmbuild RPMS tgz


install:
	@echo "Installing Nagios probes in $(DESTDIR)$(PROBES_LIBEXECDIR)..."
	@install -v -d $(DESTDIR)$(PROBES_LIBEXECDIR)
	@install -v -m 0755 src/nagios-plugins-argus.* $(DESTDIR)$(PROBES_LIBEXECDIR)
	@install -v -d $(DESTDIR)$(PROBES_LIBEXECDIR)/framework
	@install -v -m 0644 src/framework/*.py $(DESTDIR)$(PROBES_LIBEXECDIR)/framework
	@install -v -d $(DESTDIR)$(PROBES_VARDIR)

rpm: dist
	@mv -v $(name)-$(version).tar.gz $(name)-$(version).src.tar.gz
	@echo "Building RPM in $(rpmbuild_dir)"
	@mkdir -p $(rpmbuild_dir)/BUILD $(rpmbuild_dir)/RPMS \
		$(rpmbuild_dir)/SOURCES $(rpmbuild_dir)/SPECS \
		$(rpmbuild_dir)/SRPMS
	@cp -v $(name)-$(version).src.tar.gz $(rpmbuild_dir)/SOURCES/$(name)-$(version).tar.gz
	@rpmbuild -v -ba $(spec_file) --define "_topdir $(rpmbuild_dir)"


etics: rpm
	@echo "Publishing RPMs and tarballs"
	@mkdir -p tgz RPMS
	@cp -v $(name)-$(version).src.tar.gz tgz
	@test ! -f $(name)-$(version).bin.tar.gz || cp -v $(name)-$(version).bin.tar.gz tgz/$(name)-$(version).tar.gz
	@cp -rv $(rpmbuild_dir)/RPMS/* $(rpmbuild_dir)/SRPMS/* RPMS
