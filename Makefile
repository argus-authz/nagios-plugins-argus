
INSTALLDIR = /usr/libexec/grid-monitoring/probes

install:
	install -m 750 -d $(DESTDIR)$(INSTALLDIR)
	install -m 750 src/* $(DESTDIR)$(INSTALLDIR)
	# mkdir -p $(DESTDIR)$(INSTALLDIR)
	# cp src/* $(DESTDIR)$(INSTALLDIR)
	# chmod 750 $(DESTDIR)$(INSTALLDIR)/nagios-plugin-argus*
