APPNAME=kano-toolset
ORG="Kano Computing Ltd."

MSGLANGS=$(notdir $(wildcard *.po))
MSGOBJS=$(addprefix ../locale/,$(MSGLANGS:.po=/LC_MESSAGES/$(APPNAME).mo))

.PHONY: clean_locales messages

build: $(MSGOBJS)

update: $(MSGLANGS)

clean_locales:
	rm -rf ../locale

clean: clean_locales
	rm -f messages.pot

define generate-pypotfiles
grep "env python" -rl --exclude=*.py --exclude=Makefile .. > PYPOTFILES
find .. -name *.py >> PYPOTFILES
endef

define run-xgettext
xgettext -f PYPOTFILES -L Python -kN_ --force-po -o messages.pot \
    --package-name=$(APPNAME) --copyright-holder=$(ORG)
endef

define clean-up
rm PYPOTFILES
endef

messages:
	$(generate-pypotfiles)
	$(run-xgettext)
	$(clean-up)

messages.pot:
	$(generate-pypotfiles)
	$(run-xgettext)
	$(clean-up)

%.po: messages.pot
	msgmerge -N -U $*.po messages.pot
	touch $*.po

en_QQ.po: messages.pot
	../../kano-i18n/dev_locale/fake_locale messages.pot en_QQ.po

../locale/%/LC_MESSAGES/$(APPNAME).mo: clean_locales
	mkdir -p $(dir $@)
	msgfmt -c -o $@ $*.po
