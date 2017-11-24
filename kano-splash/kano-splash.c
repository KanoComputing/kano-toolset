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

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>

#include <dirent.h>
#include <limits.h>
#include <sys/stat.h>

#include "backgroundLayer.h"
#include "imageLayer.h"
#include "loadpng.h"
#include "get-start-time.h"
#include "kano-log.h"

#include "bcm_host.h"

//-------------------------------------------------------------------------

#define NDEBUG

// Animated splash windows - Frames per second and milliseconds per frame
#define FPS 15
#define MS_PER_FRAME (1000 / FPS)

// Animation keywords accepted through shebang second parameter
// this avoids the need to use hard coded paths.
typedef struct _DEFAULT_ANIMATIONS {
    char *keyword;
    char *animation_path;

} DEFAULT_ANIMATIONS;

DEFAULT_ANIMATIONS animations[] = {
    { "loader-animation", "/usr/share/kano-toolset/kano-splash/splash-animation-loader" }
};

//-------------------------------------------------------------------------

void usage(void)
{
  fprintf(stderr, "Usage: kano-splash-start [-b <RGBA>] [ -t <timeout> ] <file.png>\n");
  fprintf(stderr, "    -b - set background colour 16 bit RGBA\n");
  fprintf(stderr, "    -t - timeout in seconds\n");
  fprintf(stderr, "         e.g. 0x000F is opaque black\n");

  exit(EXIT_FAILURE);
}

DISPMANX_DISPLAY_HANDLE_T display_init(sigset_t *pwaitfor)
{
    if (!pwaitfor) {
        return -1;
    }
    else {
        // don't allow us to be killed, because this causes a videocore memory leak
        signal(SIGKILL, SIG_IGN); 
        sigaddset(pwaitfor, SIGALRM);
        sigprocmask(SIG_BLOCK, pwaitfor, NULL); // switch off ALRM in case we are sent it before we want
    }

    // Acces to dispmanx and obtaining an EGL display surface
    bcm_host_init();
    DISPMANX_DISPLAY_HANDLE_T display = vc_dispmanx_display_open(0);
    if(!display){
        kano_log_error("kano-splash: failed to open display\n");
        return 0;
    }

    return display;
}

int display_animation (DISPMANX_DISPLAY_HANDLE_T display, sigset_t *pwaitfor,
                       char *animation_directory, uint16_t timeout, uint16_t background, int looping)
{
    int error=0;
    struct dirent **namelist;
    int number_of_frames=0, current_frame_number=0;
    int32_t xOffset = 0;
    int32_t yOffset = 0;
    char *next_frame;
    struct timespec ts, frame_start, frame_end;
    long ms_frame_time=0L;
    int debug=0;


    // allocate space for the next frame filename
    next_frame = (char *) calloc(PATH_MAX, sizeof(char));
    if (!next_frame) {
        error = 2;
        goto end;
    }

    // obtain geometric information from the display surface
    DISPMANX_MODEINFO_T info;
    error = vc_dispmanx_display_get_info(display, &info);
    if (error != DISPMANX_SUCCESS) {
	error = 1;
	kano_log_error("kano-splash: failed to get display info\n");
	goto close_display;
    }

    // initialize a transparent background
    BACKGROUND_LAYER_T backgroundLayer;
    bool okay = initBackgroundLayer(&backgroundLayer, background, 0);
    if(!okay){
         kano_log_error("kano-splash: failed to init background layer\n");
	 error=1;
	 goto close_display;
    }

    // Find the first image from the animation directory
    if(debug)
        printf ("Searching for image frames at: %s\n", animation_directory);

    number_of_frames = scandir(animation_directory, &namelist, 0, alphasort);
    if (number_of_frames < 0) {
        if(debug)
            printf ("Error: could not find animation frames at: %s\n", animation_directory);
        error = 2;
        goto close_background;
    }
    else {

        current_frame_number = 0;
        do {
            sprintf(next_frame, "%s/%s", animation_directory, namelist[++current_frame_number]->d_name);

        } while(!strstr(next_frame, "png"));

        if(debug)
            printf ("loading first animation frame: %s\n", next_frame);
    }

    IMAGE_LAYER_T imageLayer;
    if (loadPng(&(imageLayer.image), next_frame) == false)
    {
        fprintf(stderr, "unable to load frame: %s\n", next_frame);
        error = 2;
        goto close_imagelayer;
        
    }
    // TODO: parametrize "1" which is the layer number
    createResourceImageLayer(&imageLayer, 1);

    // position the background and the first frame, centered on the screen
    xOffset = (info.width - imageLayer.image.width) / 2;
    yOffset = (info.height - imageLayer.image.height) / 2;
    
    DISPMANX_UPDATE_HANDLE_T update = vc_dispmanx_update_start(0);
    if (!update) {
        error = -1;
        goto close_imagelayer;
    }

    addElementBackgroundLayer(&backgroundLayer, display, update);
    addElementImageLayerOffset(&imageLayer, xOffset, yOffset, display, update);

    error = vc_dispmanx_update_submit_sync(update);
    if (error) {
        goto close_imagelayer;
    }

    // start rendering each of the frames

    while (current_frame_number++ < number_of_frames || looping) {

        if (strstr(namelist[current_frame_number]->d_name, ".png")) {

            clock_gettime(CLOCK_MONOTONIC_RAW, &frame_start);

            sprintf(next_frame, "%s/%s", animation_directory, namelist[current_frame_number]->d_name);
            if (debug)
                printf("frame #%d loading next frame: %s\n", current_frame_number, next_frame);

            // replace frame on the screen
            destroyImage(&(imageLayer.image));
            loadPng(&(imageLayer.image), next_frame);
            changeSourceAndUpdateImageLayer(&imageLayer);

            // break the animation if the signal is received - kano-stop-splash
            // poll for if the signal has been raised, return immediately in any case
            ts.tv_sec=0;
            ts.tv_nsec=0;
            if (sigtimedwait(pwaitfor,NULL, &ts) > 0) {
                // a signal was raised: stop the animation
                error = 0;
                goto close_imagelayer;
            }

            // Calculate how long it took to render the frame, in milliseconds
            clock_gettime(CLOCK_MONOTONIC_RAW, &frame_end);
            ms_frame_time = (frame_start.tv_sec == frame_end.tv_sec ?
                             frame_end.tv_nsec - frame_start.tv_nsec :
                             (1000000000  + frame_end.tv_nsec ) - frame_start.tv_nsec) / 1000000;

            if (debug) {
                printf ("frame #%d ms_frame_time=%ld fps=%d\n", current_frame_number, ms_frame_time, FPS);
            }

            // Delay the next frame to smooth the correct Frames per Second rate
            if (ms_frame_time < MS_PER_FRAME) {
                long delay = (MS_PER_FRAME - ms_frame_time) * 1000;
                if (debug) {
                    printf("ms_per_frame=%d usleep: %ld\n", MS_PER_FRAME, delay);
                }
                if (usleep (delay) < 0 && errno == EINTR) {
                    // The sleep was interrupted due to a signal,
                    // this means that kano-stop-splash wants to stop it
                    error = 0;
                    goto close_imagelayer;
                }
            }
        }
        else {
            if (debug)
                printf ("skipping file: %s\n", namelist[current_frame_number]->d_name);
        }

        if (looping && current_frame_number == number_of_frames - 1) {
            current_frame_number = 0;
        }
    }

close_imagelayer:

    destroyImageLayer(&imageLayer);

close_background:
    
    destroyBackgroundLayer(&backgroundLayer);
    
close_display:

    vc_dispmanx_display_close(display);

end:

    if (next_frame) {
        number_of_frames--;
        while(number_of_frames >= 0) {
            free(namelist[number_of_frames--]);
        }
        free(namelist);
        free(next_frame);
    }

    printf ("animation terminates with errorcode=%d\n", error);
    return error;
}

int display_image (DISPMANX_DISPLAY_HANDLE_T display, sigset_t *pwaitfor,
                   char *file, uint16_t timeout, uint16_t background)
{
    int error = 0;

    DISPMANX_MODEINFO_T info;
    int result = vc_dispmanx_display_get_info(display, &info);
    if(result != DISPMANX_SUCCESS){
	error = 1;
	kano_log_error("kano-splash: failed to get display info\n");
	goto close_display;
    }

    //---------------------------------------------------------------------

    BACKGROUND_LAYER_T backgroundLayer;
    bool okay = initBackgroundLayer(&backgroundLayer, background, 0);
    if(!okay){
         kano_log_error("kano-splash: failed to init background layer\n");
	 error=1;
	 goto close_display;
    }

    IMAGE_LAYER_T imageLayer;
    if (loadPng(&(imageLayer.image), file) == false)
    {
        kano_log_error("kano-splash: unable to load %s\n",file);
	error=1;
	goto close_background;

    }

    // TODO: parametrize "1" which is the layer number

    okay = createResourceImageLayer(&imageLayer, 1);
    if(!okay){
	 
        kano_log_error("kano-splash: unable to create resource \n");
        error=1;
	goto close_background;
    }

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
    if(!update) {
         kano_log_error("kano-splash: unable to start update\n");
	 error = 1;
	 goto close_imagelayer;
    }
	 

    bool res=addElementBackgroundLayer(&backgroundLayer, display, update);
    if(!res) {
         kano_log_error("kano-splash: unable to add background element\n");
	 error=1;
	 goto close_imagelayer;
    }

    res=addElementImageLayerCentered(&imageLayer, &info, display, update);
    if(!res) {
         kano_log_error("kano-splash: unable to add foreground element\n");
	 error=1;
	 goto close_imagelayer;
    }

    result = vc_dispmanx_update_submit_sync(update);
    if(result != DISPMANX_SUCCESS) {
         kano_log_error("kano-splash: unable to submit update\n");
	 error = 1;
	 goto close_imagelayer;
    }

    //---------------------------------------------------------------------
    // wait to be signalled with SIGARLM or timeout
    struct timespec ts;
    ts.tv_sec=timeout;
    ts.tv_nsec=0;
      
    sigtimedwait(pwaitfor,NULL, &ts);
   
    //---------------------------------------------------------------------

close_imagelayer:

    destroyImageLayer(&imageLayer);

close_background:
    
    destroyBackgroundLayer(&backgroundLayer);

close_display:
    
    result = vc_dispmanx_display_close(display);

    //---------------------------------------------------------------------

    return error;
}

//-------------------------------------------------------------------------

int main(int argc, char *argv[])
{
    uint16_t background = 0x000F;
    uint16_t timeout = 15;
    char *real_interp;
    char *file;
    char *binary;
    int is_interp;
    int status;
    int error=0;
    pid_t command_child_pid=0;
    pid_t image_child_pid=0;
    int launch_command=false;

    binary=basename(argv[0]);
    is_interp=strcmp(binary,"kano-splash")==0;
      
    if(!is_interp){
        int opt=0;
        
        while ((opt = getopt(argc, argv, "b:t:")) != -1)
        {
            switch(opt)
            {
            case 'b':
        
                background = strtol(optarg, NULL, 16);
                break;
        
            case 't':
        
                timeout = strtol(optarg, NULL, 10);
                break;
        
            default:
        
                usage();
                break;
            }
        }
        file=argv[optind];
        //---------------------------------------------------------------------
   
        if (optind >= argc)
        {
            usage();
        }
    }
    else{

        // Parse command arguments
        // As we are acting as an 'interpreter' arguments are as follows:
        // argv[0] path to this binary
        // argv[1] arguments on the #! line, if any (otherwise skipped..)
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
	  exit(1);
        }
    
        real_interp=strsep(&argv[1]," ");
          
        if(!real_interp) {
          fprintf(stderr,"real interpreter is not specified!\n");
          exit(1);
        }
    
        if(argv[1]==0){
          argv++;
          argc--;
        }
        // save back to argv for exec
        argv[0]=real_interp;

        launch_command = true;
    
    }

    image_child_pid = fork();
    if(image_child_pid==0){

        // Decide whether to start a static image or an animation splash image
        sigset_t waitfor;
        DISPMANX_DISPLAY_HANDLE_T display = display_init(&waitfor);
        if (!display) {
            return(-1);
        }
        else {

            // Find if the file refers to one of the animation keywords
            int animid;
            for (animid=0; animid < sizeof(animations) / sizeof(animations[0]); animid++) {
                if (!strcmp(file, animations[animid].keyword)) {
                    file=animations[animid].animation_path;
                    break;
                }
            }

            struct stat file_type;
            stat (file, &file_type);
            if (S_ISDIR(file_type.st_mode)) {
                // TODO: parametrize loop mode - last function option
                error = display_animation (display, &waitfor, file, timeout, background, 1);
            }
            else if (S_ISREG(file_type.st_mode)) {
                error = display_image (display, &waitfor, file, timeout, background);
            }
            else {
                error = 2; // file not found or not accessible
            }

            exit(error);
        }
    }

    if(launch_command){
	// save pid info so child can halt the splash
	char pid_str[32];
	char start_time_str[32];
	snprintf(pid_str,32,"%u",image_child_pid);
	snprintf(start_time_str,32,"%llu",get_process_start_time(image_child_pid));
	// set environment variables for stopping the splash
	setenv("SPLASH_PID",pid_str,1);
	setenv("SPLASH_START_TIME",start_time_str,1);

	// launch command
        command_child_pid=fork();
        if(command_child_pid==0){
          execvp(real_interp,argv);	
        }
    }      
    error = waitpid(image_child_pid, &status, 0);

    if(command_child_pid){
      int r = waitpid(command_child_pid, &status, 0);
      if(r){
        kano_log_error("kano-splash: error from child\n");
      }
    }
    return error;
}
