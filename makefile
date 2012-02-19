
# N9 Personal Web Server (http://thp.io/2012/serverr/)
# Copyright (c) 2012 Thomas Perl <thp.io/about>

APP_NAME = serverr

all:
	true

install:
	mkdir -p $(DESTDIR)/opt/$(APP_NAME)/
	cp *.qml *.png $(DESTDIR)/opt/$(APP_NAME)/
	mkdir -p $(DESTDIR)/opt/$(APP_NAME)/bin/
	cp $(APP_NAME).py $(DESTDIR)/opt/$(APP_NAME)/bin/
	chmod +x $(DESTDIR)/opt/$(APP_NAME)/bin/$(APP_NAME).py
	mkdir -p $(DESTDIR)/usr/share/applications/
	cp $(APP_NAME).desktop $(DESTDIR)/usr/share/applications/

.PHONY: all install

