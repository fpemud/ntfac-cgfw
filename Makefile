prefix=/usr

all:

clean:
	fixme

install:
	install -d -m 0755 "$(DESTDIR)/$(prefix)/libexec"
	install -m 0755 ntfac-cgfw "$(DESTDIR)/$(prefix)/libexec"

	install -d -m 0755 "$(DESTDIR)/etc/ntfac-cgfw"
	cp -r etc/* "$(DESTDIR)/etc/ntfac-cgfw"
	find "$(DESTDIR)/etc/ntfac-cgfw" -type f | xargs chmod 600

uninstall:
	rm -f "$(DESTDIR)/$(prefix)/libexec/ntfac-cgfw"
	rm -rf "$(DESTDIR)/etc/ntfac-cgfw"

.PHONY: all clean install uninstall
