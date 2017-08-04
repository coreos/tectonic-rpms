syncdir := /tmp/sync


all: build

rpmbuildopts ?= --rpmbuild-options '-D "%_buildhost buildhost.tectonic.coreos.systems"'

build:
	tito build --rpmbuild-options '-D "%_buildhost buildhost.tectonic.coreos.systems" ' --rpm  --dist=.el7 -o out $(rpmbuildopts)

build-test:
	tito build --rpmbuild-options '-D "%_buildhost buildhost.tectonic.coreos.systems" ' --rpm  --dist=.el7 -o out --test --debug

collect:
	mkdir -p $(syncdir)/{SRPMs,x86_64}/Packages
	cp out/$(pkg)-$(pkgrel)$(DIST).src.rpm $(syncdir)/SRPMs/Packages/
	cp out/$(pkg)-$(pkgrel)$(DIST).x86_64.rpm $(syncdir)/x86_64/Packages/
	cp out/$(pkg)-debuginfo-$(pkgrel)$(DIST).x86_64.rpm $(syncdir)/x86_64/Packages/


clean:
	rm -rf ./*.src.rpm noarch/
