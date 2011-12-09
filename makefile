
INSTALLDIR = $(DESTDIR)/usr/libexec/grid-monitoring/probes/

install:
	mkdir -p $(INSTALLDIR)
	cp src/* $(INSTALLDIR)
	chown casutt:middle $(INSTALLDIR)/nagios-plugin-argus*
	chmod 750 $(INSTALLDIR)/nagios-plugin-argus*
