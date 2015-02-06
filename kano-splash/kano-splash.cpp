// kano-splash.cpp
//
// Copyright (C) 2015 Kano Computing Ltd.
// License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
//
// Derived from http://git.enlightenment.org/legacy/imlib2.git/tree/src/bin/imlib2_view.c
// (See http://git.enlightenment.org/legacy/imlib2.git/tree/AUTHORS )
// Display a splash window and wait for the app to tell us to stop displaying it (or a timeout).
// 


#include <X11/Xlib.h>
#include <X11/extensions/XShm.h>
#include <X11/Xutil.h>
#include <X11/extensions/shape.h>
#include <X11/Xatom.h>
#include <X11/Xos.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>
#include <errno.h>
#include "Imlib2.h"
#include "get-start-time.h"

Display            *disp;
Window              win;
Pixmap              pm = 0;
Visual             *vis;
Colormap            cm;
int                 depth;
int                 image_width = 0, image_height = 0;
int                 window_width = 0, window_height = 0;
double              scale = 1.;
Imlib_Image         bg_im = NULL;

static Atom         ATOM_WM_DELETE_WINDOW = None;
static Atom         ATOM_WM_PROTOCOLS = None;

#define SCALE(x) (int)(scale * (x) + .5)


int
main(int argc, char **argv)
{
  char               *s;
  Imlib_Image        *im = NULL;
  char               *file = NULL;
  int                 no = 1;

  for (no = 1; no < argc; no++)
    {
      s = argv[no];
      if (*s++ != '-')
	break;
      switch (*s)
	{
	default:
	  break;
	case 's':            /* Scale (window size wrt. image size) */
	  if (++no < argc)
	    scale = atof(argv[no]);
	  break;
	}
    }

  if (no >= argc)
    {
      fprintf(stderr, "imlib2_view [-s <scale factor>] file...\n");
      return 1;
    }

  disp = XOpenDisplay(NULL);
  if (!disp)
    {
      fprintf(stderr, "Cannot open display\n");
      return 1;
    }

  vis = DefaultVisual(disp, DefaultScreen(disp));
  depth = DefaultDepth(disp, DefaultScreen(disp));
  cm = DefaultColormap(disp, DefaultScreen(disp));

  win = XCreateSimpleWindow(disp, DefaultRootWindow(disp), 0, 0, 10, 10,
			    0, 0, 0);


  // Remove window decorations
  Atom type = XInternAtom(disp, "_NET_WM_WINDOW_TYPE", False);
  Atom value = XInternAtom(disp, "_NET_WM_WINDOW_TYPE_SPLASH", False);
  XChangeProperty(disp, win, type, XA_ATOM, 32, PropModeReplace, reinterpret_cast<unsigned char*>(&value), 1);


  ATOM_WM_PROTOCOLS = XInternAtom(disp, "WM_PROTOCOLS", False);
  ATOM_WM_DELETE_WINDOW = XInternAtom(disp, "WM_DELETE_WINDOW", False);
  XSetWMProtocols(disp, win, &ATOM_WM_DELETE_WINDOW, 1);

  imlib_context_set_display(disp);
  imlib_context_set_visual(vis);
  imlib_context_set_colormap(cm);
  imlib_context_set_drawable(win);

  file = argv[no];
  im = imlib_load_image(file);
  if (!im)
    {
      fprintf(stderr, "Image format not available\n");
      exit(0);
    }
  imlib_context_set_image(im);


  imlib_context_set_drawable(pm);
  imlib_context_set_anti_alias(0);
  imlib_context_set_dither(0);
  imlib_context_set_blend(0);
  int                 x, y, onoff;

  image_width = imlib_image_get_width();
  image_height = imlib_image_get_height();
  window_width = SCALE(image_width);
  window_height = SCALE(image_height);
  pm = XCreatePixmap(disp, win, window_width, window_height, depth);
  imlib_context_set_drawable(pm);
  imlib_context_set_image(im);
  XSetWindowBackgroundPixmap(disp, win, pm);
  XResizeWindow(disp, win, window_width, window_height);
  XMapWindow(disp, win);
  XSync(disp, False);


  imlib_context_set_anti_alias(0);
  imlib_context_set_dither(0);

  int                 up_wx, up_wy, up_ww, up_wh;
  up_wx = SCALE(0);
  up_wy = SCALE(0);
  up_ww = SCALE(image_width);
  up_wh = SCALE(image_height);
  imlib_context_set_blend(0);
  imlib_render_image_part_on_drawable_at_size(0, 0,
					      image_width, image_height,
					      up_wx, up_wy, up_ww, up_wh);
  XClearArea(disp, win, up_wx, up_wy, up_ww, up_wh, False);
  XFlush(disp);


  //system("date +%s.%N");
  sleep(15);
  
  return 0;
}
