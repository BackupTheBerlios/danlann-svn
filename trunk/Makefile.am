SUBDIRS = bin css doc examples js src

tests:
	PYTHONPATH=src python src/danlann/test/__init__.py -v

installcheck-local:
	PYTHONPATH=$(DESTDIR)/$(pythondir) python $(DESTDIR)/$(pythondir)/danlann/test/__init__.pyc -v
