
all: kano-launcher kano-kill-ns

LIBS=-L../kano-logging -lkano-logging
INCLUDES=-I../kano-logging 
kano-launcher:
	gcc -std=c99 -D_BSD_SOURCE -gdwarf-2 $(INCLUDES) kano-launcher.c $(LIBS) -o kano-launcher 

kano-kill-ns:
	gcc -std=c99 -D_BSD_SOURCE -gdwarf-2 $(INCLUDES) kano-kill-ns.c $(LIBS) -o kano-kill-ns
