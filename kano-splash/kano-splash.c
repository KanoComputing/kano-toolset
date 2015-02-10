//-------------------------------------------------------------------------
//
// The MIT License (MIT)
//
// Copyright (c) 2013 Andrew Duncan
// Copyright (c) 2015 Kano Computing Ltd.
//
// Permission is hereby granted, free of charge, to any person obtaining a
// copy of this software and associated documentation files (the
// "Software"), to deal in the Software without restriction, including
// without limitation the rights to use, copy, modify, merge, publish,
// distribute, sublicense, and/or sell copies of the Software, and to
// permit persons to whom the Software is furnished to do so, subject to
// the following conditions:
//
// The above copyright notice and this permission notice shall be included
// in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
// MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
// IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
// CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
// TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
// SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
//
//-------------------------------------------------------------------------

#define _GNU_SOURCE

#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>

#include "backgroundLayer.h"
#include "imageLayer.h"
#include "loadpng.h"
#include "get-start-time.h"

#include "bcm_host.h"

//-------------------------------------------------------------------------

#define NDEBUG

//-------------------------------------------------------------------------


//-------------------------------------------------------------------------


//-------------------------------------------------------------------------

int main(int argc, char *argv[])
{
    uint16_t background = 0x000F;
    char *real_interp;
    char *file;

    // Parse command arguments
    // As we are acting as an 'interpreter' arguments are as follows:
    // argv[0] path to this binary
    // argv[1] arguments on the #! line
    // argv[2] the script we are called on
    // argv[3..] command line arguments

    // we expect argv[1] to contain the filename followed by the next interpreter we want to invoke and
    // its arguments. so we extract these and then do the following mapping:

    // splash file = arg[1][0]
    // argv[0] = argv[1][1..]
    // 
    // This leaves the command line 
    

    background=0; // full transparency

    if(argc<2) {
      fprintf(stderr,"Insufficient arguments\n");
      exit(1);
    }

    file=strsep(&argv[1]," ");

    if(!file) {
      fprintf(stderr,"filename is NULL \n");      
    }

    real_interp=strsep(&argv[1]," ");
      
    if(!real_interp) {
      fprintf(stderr,"real interpreter is not specified!\n");
      exit(1);
    }

    // save back to argv for exec
    argv[0]=real_interp;

    // save pid info so child can halt the splash

    char pid_str[32];
    char start_time_str[32];
    pid_t mypid=getpid();
    snprintf(pid_str,32,"%u",mypid);
    snprintf(start_time_str,32,"%llu",get_process_start_time(mypid));
    setenv("SPLASH_PID",pid_str,1);
    setenv("SPLASH_START_TIME",start_time_str,1);
    pid_t pid=fork();
    if(pid==0){
      execvp(real_interp,argv);	
    }
    
    //---------------------------------------------------------------------

    bcm_host_init();

    //---------------------------------------------------------------------

    DISPMANX_DISPLAY_HANDLE_T display = vc_dispmanx_display_open(0);
    assert(display != 0);

    //---------------------------------------------------------------------

    DISPMANX_MODEINFO_T info;
    int result = vc_dispmanx_display_get_info(display, &info);
    assert(result == 0);

    //---------------------------------------------------------------------

    BACKGROUND_LAYER_T backgroundLayer;
    initBackgroundLayer(&backgroundLayer, background, 0);

    IMAGE_LAYER_T imageLayer;
    if (loadPng(&(imageLayer.image), file) == false)
    {
        fprintf(stderr, "unable to load %s\n", file);
    }
    createResourceImageLayer(&imageLayer, 1);

    //---------------------------------------------------------------------

    int32_t outWidth = imageLayer.image.width;
    int32_t outHeight = imageLayer.image.height;

    if ((imageLayer.image.width > info.width) &&
        (imageLayer.image.height > info.height))
    {
    }
    else
    {
        double imageAspect = (double)imageLayer.image.width
                                     / imageLayer.image.height;
        double screenAspect = (double)info.width / info.height;

        if (imageAspect > screenAspect)
        {
            outWidth = info.width;
            outHeight = (imageLayer.image.height * info.width)
                         / imageLayer.image.width; 
        }
        else
        {
            outWidth = (imageLayer.image.width * info.height)
                        / imageLayer.image.height; 
            outHeight = info.height;
        }
    }

    vc_dispmanx_rect_set(&(imageLayer.srcRect),
                         0 << 16,
                         0 << 16,
                         imageLayer.image.width << 16,
                         imageLayer.image.height << 16);

    vc_dispmanx_rect_set(&(imageLayer.dstRect),
                         (info.width - outWidth) / 2,
                         (info.height - outHeight) / 2,
                         outWidth,
                         outHeight);

    //---------------------------------------------------------------------

    DISPMANX_UPDATE_HANDLE_T update = vc_dispmanx_update_start(0);
    assert(update != 0);

    addElementBackgroundLayer(&backgroundLayer, display, update);
    addElementImageLayerCentered(&imageLayer, &info, display, update);

    result = vc_dispmanx_update_submit_sync(update);
    assert(result == 0);

    //---------------------------------------------------------------------
    

    sleep(15);
    //---------------------------------------------------------------------


    //---------------------------------------------------------------------

    destroyBackgroundLayer(&backgroundLayer);
    destroyImageLayer(&imageLayer);

    //---------------------------------------------------------------------

    result = vc_dispmanx_display_close(display);
    assert(result == 0);

    //---------------------------------------------------------------------

    return 0;
}

