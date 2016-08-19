#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Build file for libkano_networking
#

PLATFORM := $(shell uname)

ifeq ($(PLATFORM), Linux)
	SONAME_FLAG = -soname
	SONAME = libkano_networking.so
	LD_TYPE = -shared
else ifeq ($(PLATFORM), Darwin)
	SONAME_FLAG = -install_name
	SONAME = libkano_networking.dylib
	LD_TYPE = -dynamiclib
endif

CFLAGS += -Wall -Wextra -g -fPIC -c
LDFLAGS += $(LD_TYPE) -Wl,$(SONAME_FLAG),$(SONAME)
INCLUDES += -I./includes
OBJS = ifaces.so

OUTDIR = release
DEBUG_OUTDIR = debug


all: ensure-dir $(SONAME)

debug: CFLAGS += -DDEBUG -g
debug: OUTDIR=$(DEBUG_OUTDIR)
debug: $(SONAME)

ensure-dir:
	mkdir -p $(OUTDIR)
	mkdir -p $(DEBUG_OUTDIR)

$(SONAME): $(OBJS)
	$(CC) $(LDFLAGS) $(addprefix $(OUTDIR)/, $?) -o $(OUTDIR)/$@

%.so: src/%.c
	$(CC) $(CFLAGS) $(INCLUDES) $< -o $(OUTDIR)/$@


clean: clean-release clean-debug

clean-release:
	@rm -f $(OUTDIR)/$(OBJS)
	@rm -f $(OUTDIR)/$(SONAME)

clean-debug:
	@rm -f $(DEBUG_OUTDIR)/$(OBJS)
	@rm -f $(DEBUG_OUTDIR)/$(SONAME)

link: all  # for Mac OS
	mkdir -p /usr/local/include/kano
	ln -fs `pwd`/includes/kano/* /usr/local/include/kano
	ln -fs `pwd`/release/$(SONAME) /usr/local/lib

unlink: all  # for Mac OS
	rm -rf /usr/local/include/kano/networking
	rm -f /usr/local/lib/$(SONAME)
