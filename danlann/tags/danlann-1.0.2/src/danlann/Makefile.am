SUBDIRS = test

EXTRA_DIST = config.py.in
CLEANFILES = config.py

pkgpython_PYTHON = bc.py \
				config.py \
				filemanager.py \
				generator.py \
				__init__.py \
				parser.py \
				template.py

do_subst = sed -e 's,[@]datadir[@],$(datadir),g' \
	-e 's,[@]VERSION[@],$(VERSION),g'

config.py: config.py.in Makefile
	$(do_subst) < $(srcdir)/config.py.in > config.py
