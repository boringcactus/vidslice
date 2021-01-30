# vidslice

video manipulator wrapping youtube-dl and ffmpeg

![screenshot of vidslice demonstrating options](screenshot.png)

## Installing
1. Make sure you have [Python](https://www.python.org/downloads/) installed.
2. [Download vidslice](https://github.com/boringcactus/vidslice/releases/latest).

   a. If you already have ffmpeg and youtube-dl installed, download `vidslice.pyw`.

   b. If you don't, download `vidslice-full-win.zip`. (If you're not on Windows, you'll have to install ffmpeg and
   youtube-dl yourself, sorry.)

## Using
If you already have a video file in a format supported by ffmpeg (which is most of them), you can use the "Browse" button in the Sources panel to load in your video.
If you want to download something from YouTube or anywhere else listed [here](https://rg3.github.io/youtube-dl/supportedsites.html), paste the URL in the URL box and hit "Download".

Properties of the video are listed in the Options panel; you can check the Edit box for a property to set a new value for it.
You can't edit all three time fields, since two of them together always determine the third one.

The Output panel lets you specify where you want the output to go.
You can use any format ffmpeg supports.
For a silent video, which is just a better GIF as far as platforms like Telegram are concerned, check the "Silence" box.
To use absurdly high compression settings, which might not even work depending on your output format, check the "Compress beyond recognition" box.

The "Run" button will simply run the conversion; "Run & Preview" will show your output afterwards; "Run & Quit" will quit vidslice afterwards.
