SUBDIRS = bin css doc examples js src

tests:
	PYTHONPATH=src nosetests src/danlann/test/

installcheck-local:
	PYTHONPATH=$(DESTDIR)/$(pythondir) python $(DESTDIR)/$(pythondir)/danlann/test/__init__.pyc -v
