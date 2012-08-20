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

name=nagios-plugins-argus

version=1.0.1
release=1

PROBES_NAMESPACE = $(name)
PROBES_LIBEXECDIR = /usr/libexec/grid-monitoring/probes/$(PROBES_NAMESPACE)
PROBES_VARDIR = /var/lib/grid-monitoring/$(PROBES_NAMESPACE)

spec_file=fedora/$(name).spec

rpmbuild_dir=$(CURDIR)/rpmbuild
debbuild_dir = $(CURDIR)/debbuild
tmp_dir=$(CURDIR)/tmp

.PHONY: clean spec package dist rpm deb install

all: 
	@echo "Nothing to compile ;)"

clean:
	rm -rf target $(rpmbuild_dir) $(debbuild_dir) $(tmp_dir) *.tar.gz tgz RPMS $(spec_file)


spec:
	@echo "Setting version and release in spec file: $(version)-$(release)"
	sed -e 's#@@VERSION@@#$(version)#g' -e 's#@@RELEASE@@#$(release)#g' $(spec_file).in > $(spec_file)


dist: spec
	@echo "Packaging sources"
	test ! -d $(tmp_dir) || rm -fr $(tmp_dir)
	mkdir -p $(tmp_dir)/$(name)-$(version)
	cp Makefile $(tmp_dir)/$(name)-$(version)
	cp COPYRIGHT LICENSE README.md CHANGELOG $(tmp_dir)/$(name)-$(version)
	cp -r fedora $(tmp_dir)/$(name)-$(version)
	cp -r debian $(tmp_dir)/$(name)-$(version)
	cp -r src $(tmp_dir)/$(name)-$(version)
	test ! -f $(name)-$(version).tar.gz || rm $(name)-$(version).tar.gz
	tar -C $(tmp_dir) -czf $(name)-$(version).tar.gz $(name)-$(version)
	rm -fr $(tmp_dir)


install:
	@echo "Installing Nagios probes in $(DESTDIR)$(PROBES_LIBEXECDIR)..."
	install -d $(DESTDIR)$(PROBES_LIBEXECDIR)
	install -m 0755 src/nagios-plugins-argus.* $(DESTDIR)$(PROBES_LIBEXECDIR)
	install -d $(DESTDIR)$(PROBES_LIBEXECDIR)/framework
	install -m 0644 src/framework/*.py $(DESTDIR)$(PROBES_LIBEXECDIR)/framework
	install -d $(DESTDIR)$(PROBES_VARDIR)

rpm:
	test -f $(name)-$(version).tar.gz || make dist
	@echo "Building RPM and SRPM in $(rpmbuild_dir)"
	mv $(name)-$(version).tar.gz $(name)-$(version).src.tar.gz
	mkdir -p $(rpmbuild_dir)/BUILD $(rpmbuild_dir)/RPMS $(rpmbuild_dir)/SOURCES $(rpmbuild_dir)/SPECS $(rpmbuild_dir)/SRPMS
	cp $(name)-$(version).src.tar.gz $(rpmbuild_dir)/SOURCES/$(name)-$(version).tar.gz
	rpmbuild --nodeps -v -ba $(spec_file) --define "_topdir $(rpmbuild_dir)"


deb:
	test -f $(name)-$(version).tar.gz || make dist
	@echo "Building Debian package in $(debbuild_dir)"
	mv $(name)-$(version).tar.gz $(name)-$(version).src.tar.gz
	mkdir -p $(debbuild_dir)
	cp $(name)-$(version).src.tar.gz $(debbuild_dir)/$(name)_$(version).orig.tar.gz
	tar -C $(debbuild_dir) -xzf $(name)-$(version).src.tar.gz
	cd $(debbuild_dir)/$(name)-$(version) && debuild -us -uc 


etics:
	@echo "Publish RPMS, SRPMS and tarball"
	test -f $(rpmbuild_dir)/SRPMS/$(name)-$(version)-*.src.rpm
	mkdir -p tgz RPMS
	cp target/*.tar.gz tgz
	cp -r $(rpmbuild_dir)/RPMS/* $(rpmbuild_dir)/SRPMS/* RPMS

