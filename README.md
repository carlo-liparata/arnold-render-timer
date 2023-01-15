# arnold-render-timer
A python script to track how much time your render in the renderview takes

I find this very useful whenever I'm doing lookdev or lighting, both to optimize and to have a rough idea of how much a frame takes, without having to fully render it to disk. 

It features a self-stopping timer, which works by checking the hick.exe process cpu consumption percentage.

The UI is quite straightforward, the "Update Render" button acts as a stop+start render. It's there to restart the render when loading a new geomery or changing values that need the render to be restarted to be updated in the render view. 

Tested on Houdini 19.0 and 19.5, Arnold 6 and 7.
