
all: kano-launcher kano-kill-ns

LIBS=-L../libs/kano-c-logging/release/ -lkano_c_logging
INCLUDES=-I../libs/kano-c-logging/includes
kano-launcher:
	gcc -std=c99 -D_BSD_SOURCE -gdwarf-2 $(INCLUDES) kano-launcher.c $(LIBS) -o kano-launcher 

kano-kill-ns:
	gcc -std=c99 -D_BSD_SOURCE -gdwarf-2 $(INCLUDES) kano-kill-ns.c $(LIBS) -o kano-kill-ns
