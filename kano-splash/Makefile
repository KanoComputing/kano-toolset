#kano-get-start-time/* kano-get-start-time.c
# 
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://opensource.org/licenses/MIT
# 
# Build file for kano-splash and related utilities.
#
OBJS=kano-splash.o backgroundLayer.o imageLayer.o \
	 loadpng.o image.o get-start-time.o
BIN= kano-splash kano-get-start-time
CFLAGS+=-Wall -g -O3  $(shell libpng-config --cflags)
LDFLAGS+=-L/opt/vc/lib/ -lbcm_host -lm $(shell libpng-config --ldflags) -L../kano-logging -lkano-logging

INCLUDES+=-I/opt/vc/include/ -I/opt/vc/include/interface/vcos/pthreads -I/opt/vc/include/interface/vmcs_host/linux -I../kano-logging 

all: $(BIN)

%.o: %.c
	@rm -f $@ 
	$(CC) $(CFLAGS) $(INCLUDES) -g -c $< -o $@ -Wno-deprecated-declarations

kano-splash: $(OBJS)
	$(CC) -o $@ -Wl,--whole-archive $(OBJS) $(LDFLAGS) -Wl,--no-whole-archive -rdynamic

clean:
	@rm -f $(OBJS)
	@rm -f $(BIN)



kano-get-start-time: kano-get-start-time.c get-start-time.c
	$(CC) -g $^  -o $@
