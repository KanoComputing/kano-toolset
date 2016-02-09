#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Build file for libkano_networking
#

SONAME=libkano_networking.so.1
CFLAGS+=-Wall -Wextra -O3 -fPIC -c
LDFLAGS+=-shared -Wl,-soname,$(SONAME)
INCLUDES+=-I./includes
OBJS=ifaces.so

all: $(SONAME)

$(SONAME): $(OBJS)
	$(CC) $(LDFLAGS) $(INCLUDES) $< -o $@

%.so: src/%.c
	$(CC) $(CFLAGS) $(INCLUDES) $< -o $@

clean:
	@rm -f $(OBJS)
	@rm -f $(SONAME)
