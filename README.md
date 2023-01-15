# arnold-render-timer
A python script to track how much time your render in the renderview takes

I find this very useful whenever I'm doing lookdev or lighting, both to optimize and to have a rough idea of how much a frame takes, without having to fully render it to disk. 

It features a self-stopping timer, which works by checking the hick.exe process cpu consumption percentage.
