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
# ETICS directories
tgz_dir=$(CURDIR)/tgz
rpm_dir=$(CURDIR)/RPMS
deb_dir=$(CURDIR)/debs

.PHONY: clean spec dist package install srpm rpm deb deb-src

clean:
	rm -rf target $(rpmbuild_dir) $(debbuild_dir) $(tmp_dir) *.tar.gz $(tgz_dir) $(rpm_dir) $(deb_dir) $(spec_file)

all: 
	@echo "Nothing to compile ;)"
	@echo "make DESTDIR=<destdir> install"

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

pre_rpmbuild:
	test -f $(name)-$(version).tar.gz || make dist
	@echo "Preparing for rpmbuild in $(rpmbuild_dir)"
	mv $(name)-$(version).tar.gz $(name)-$(version).src.tar.gz
	mkdir -p $(rpmbuild_dir)/BUILD $(rpmbuild_dir)/RPMS $(rpmbuild_dir)/SOURCES $(rpmbuild_dir)/SPECS $(rpmbuild_dir)/SRPMS
	cp $(name)-$(version).src.tar.gz $(rpmbuild_dir)/SOURCES/$(name)-$(version).tar.gz


srpm: pre_rpmbuild
	@echo "Building SRPM in $(rpmbuild_dir)"
	rpmbuild --nodeps -v -bs $(spec_file) --define "_topdir $(rpmbuild_dir)"


rpm: pre_rpmbuild
	@echo "Building RPM/SRPM in $(rpmbuild_dir)"
	rpmbuild --nodeps -v -ba $(spec_file) --define "_topdir $(rpmbuild_dir)"


pre_debbuild:
	test -f $(name)-$(version).tar.gz || make dist
	@echo "Prepare for Debian building in $(debbuild_dir)"
	mv $(name)-$(version).tar.gz $(name)-$(version).src.tar.gz
	mkdir -p $(debbuild_dir)
	cp $(name)-$(version).src.tar.gz $(debbuild_dir)/$(name)_$(version).orig.tar.gz
	tar -C $(debbuild_dir) -xzf $(name)-$(version).src.tar.gz


deb: pre_debbuild
	@echo "Building Debian package in $(debbuild_dir)"
	cd $(debbuild_dir)/$(name)-$(version) && debuild -us -uc 


deb-src: pre_debbuild
	@echo "Building Debian source package in $(debbuild_dir)"
	cd $(debbuild_dir) && dpkg-source -b $(name)-$(version)


etics:
	@echo "Publish SRPM/RPM/Debian/tarball"
	mkdir -p $(rpm_dir) $(tgz_dir) $(deb_dir)
	test ! -f $(name)-$(version).src.tar.gz || cp -v $(name)-$(version).src.tar.gz $(tgz_dir)
	test ! -f $(rpmbuild_dir)/SRPMS/$(name)-$(version)-*.src.rpm || cp -v $(rpmbuild_dir)/SRPMS/$(name)-$(version)-*.src.rpm $(rpm_dir)
	if [ -f $(rpmbuild_dir)/RPMS/*/$(name)-$(version)-*.rpm ] ; then \
		cp -v $(rpmbuild_dir)/RPMS/*/$(name)-$(version)-*.rpm $(rpm_dir) ; \
		test ! -d $(tmp_dir) || rm -fr $(tmp_dir) ; \
		mkdir -p $(tmp_dir) ; \
		cd $(tmp_dir) ; \
		rpm2cpio $(rpmbuild_dir)/RPMS/*/$(name)-$(version)-*.rpm | cpio -idm ; \
		tar -C $(tmp_dir) -czf $(name)-$(version).tar.gz * ; \
		mv -v $(name)-$(version).tar.gz $(tgz_dir) ; \
		rm -fr $(tmp_dir) ; \
	fi
	test ! -f $(debbuild_dir)/$(name)_$(version)-*.dsc || cp -v $(debbuild_dir)/$(name)_$(version)-*.dsc $(deb_dir)
	test ! -f $(debbuild_dir)/$(name)_$(version)-*.debian.tar.gz || cp -v $(debbuild_dir)/$(name)_$(version)-*.debian.tar.gz $(deb_dir)
	test ! -f $(debbuild_dir)/$(name)_$(version).orig.tar.gz || cp -v $(debbuild_dir)/$(name)_$(version).orig.tar.gz $(deb_dir)
	if [ -f $(debbuild_dir)/$(name)_$(version)-*.deb ] ; then \
		cp -v $(debbuild_dir)/$(name)_$(version)-*.deb $(deb_dir) ; \
		test ! -d $(tmp_dir) || rm -fr $(tmp_dir) ; \
		mkdir -p $(tmp_dir) ; \
		dpkg -x $(debbuild_dir)/$(name)_$(version)-*.deb $(tmp_dir) ; \
		cd $(tmp_dir) ; \
		tar -C $(tmp_dir) -czf $(name)-$(version).tar.gz * ; \
		mv -v $(name)-$(version).tar.gz $(tgz_dir) ; \
		rm -fr $(tmp_dir) ; \
	fi

