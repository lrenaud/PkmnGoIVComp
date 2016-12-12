# PkmnGoIVComp
A 3rd Party, Python IV Computer library for Pokemon Go
**This project has no affilation with Nintendo, Niantic, or any offical Pokemon related company**

## Structure
The core structure of this helper class is written as a helper to generate objects for a given 
pokemon based upon it's name, CP, HP, dust price, and your trainer level at time of capture or last,
power up. (Hooray, I just found a use-case bug).

I want to push this out as quickly as I can, as I've sat on this for too long as is. For now you'll
find an example for using this script in the repo itself that breaks down a simple use case for the
class.

## Props to /u/aggixx on /r/TheSilphRoad
I have to point out that I ripped the core structure of this tool from the Google Docs based
implemetnation posted on Reddit back in the Summer of 2016. My complaint was that even on a beefy
computer the javascript implementation could bring my web browser to it's knees, to say nothing if
I was on a laptop or anything slightly old or memory limited.

That said, this code is entirely written from scratch even though it's core inspiration comes from
/u/aggixx. I don't want to step on anyone's toes, I just wanted a tool that was a bit more flexible.

## Interactive Use
If you want to tinker with the tool line by line rather than constantly re-running your checks, then
the script can be called interactively and the results will then be directly browsable via the
python3 interactive shell.
```
$ python3 -i example.py
```

Enjoy.
 -Luke
