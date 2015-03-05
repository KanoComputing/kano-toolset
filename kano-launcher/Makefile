
all: kano-launcher kano-kill-ns



kano-launcher:
	gcc -std=c99 -D_BSD_SOURCE -gdwarf-2 kano-launcher.c kano-log.c -o kano-launcher 

kano-kill-ns:
	gcc -std=c99 -D_BSD_SOURCE -gdwarf-2 kano-kill-ns.c kano-log.c -o kano-kill-ns
