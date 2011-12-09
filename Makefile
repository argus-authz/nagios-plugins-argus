
INSTALLDIR = /usr/libexec/grid-monitoring/probes

install:
	mkdir -p $(DESTDIR)$(INSTALLDIR)
	cp src/* $(DESTDIR)$(INSTALLDIR)
	chmod 750 $(DESTDIR)$(INSTALLDIR)/nagios-plugin-argus*
