

install:
	cp src/* /usr/libexec/grid-monitoring/probes/
	chown nagios:nagios /usr/libexec/grid-monitoring/probes/nagios-plugin-argus*
	chmod 750 /usr/libexec/grid-monitoring/probes/nagios-plugin-argus*
