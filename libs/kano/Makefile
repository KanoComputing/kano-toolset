#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Build file for libkano
#

PLATFORM := $(shell uname)

ifeq ($(PLATFORM), Linux)
	SONAME_FLAG = -soname
	SONAME = libkano.so
	LD_TYPE = -shared
else ifeq ($(PLATFORM), Darwin)
	SONAME_FLAG = -install_name
	SONAME = libkano.dylib
	LD_TYPE = -dynamiclib
endif

CXXFLAGS += -Wall -Wextra -O3 -fPIC -c -std=c++11 `python-config --cflags`
LDFLAGS += $(LD_TYPE) -Wl,$(SONAME_FLAG),$(SONAME) `python-config --ldflags` -lkano_python
INCLUDES += -I./includes
OBJS = \
	kano_network.so \
	kano_utils_audio.so
DEPS = \
	kano-toolset/libs/kano-python

OUTDIR = release
DEBUG_OUTDIR = debug


ifeq ($(PLATFORM), Darwin)
all: ensure-dir $(DEPS) $(SONAME)
else
all: ensure-dir $(SONAME)
endif

debug: CXXFLAGS += -DDEBUG -g
debug: OUTDIR = $(DEBUG_OUTDIR)
debug: $(SONAME)

ensure-dir:
	mkdir -p $(OUTDIR)
	mkdir -p $(DEBUG_OUTDIR)

$(DEPS):
	make -C ../../../$@ link

$(SONAME): $(OBJS)
	$(CXX) $(LDFLAGS) $(addprefix $(OUTDIR)/, $?) -o $(OUTDIR)/$@

%.so: src/%.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) $< -o $(OUTDIR)/$@


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
	rm -rf /usr/local/include/kano/kano
	rm -f /usr/local/lib/$(SONAME)
