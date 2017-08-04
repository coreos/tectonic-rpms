RPMS = rkt tectonic-release tectonic-worker

BUILDRPMS = $(RPMS:%=build-%)
LINTRPMS = $(RPMS:%=lint-%)
CLEANRPMS = $(RPMS:%=clean-%)

rpmbuildopts ?= --rpmbuild-options '-D "%_buildhost buildhost.tectonic.coreos.systems"'


all: $(BUILDRPMS)
$(RPMS): $(BUILDRPMS)
$(BUILDRPMS):
	rpmlint -f rpmlint-config  $(@)/$(@).spec
	$(MAKE) -C $(@:build-%=%)

clean: $(CLEANRPMS)
$(CLEANRPMS):
	$(MAKE) -C $(@:clean-%=%) clean

lint: $(LINTRPMS)
$(LINTRPMS):
	$(MAKE) -C $(@:lint-%=%) lint

.PHONY: subdirs $(RPMS)
.PHONY: subdirs $(BUILDRPMS)
.PHONY: subdirs $(LINTRPMS)
.PHONY: subdirs $(CLEANRPMS)
.PHONY: all clean 
