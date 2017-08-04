all: build

rpmbuildopts ?= --rpmbuild-options '-D "%_buildhost buildhost.tectonic.coreos.systems"'


build:
	tito build --rpmbuild-options '-D "%_buildhost buildhost.tectonic.coreos.systems"' --rpm  --dist=.el7 -o . $(rpmbuildopts)

build-test:
	tito build --rpmbuild-options '-D "%_buildhost buildhost.tectonic.coreos.systems"' --rpm  --dist=.el7 -o . --test --debug

clean:
	rm -rf ./*.src.rpm noarch/
