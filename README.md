# vidslice

video manipulator wrapping youtube-dl and ffmpeg

![screenshot of vidslice demonstrating options](screenshot.png)

## Installing
1. Download the .zip for your preferred OS [here](https://github.com/boringcactus/vidslice/releases/latest) and extract it somewhere convenient.
2. If you don't have it already, [download ffmpeg](https://ffmpeg.org/download.html#get-packages) (if you're on Windows, you want Windows Builds and then the default options are fine) and make sure ffmpeg.exe, ffprobe.exe, and ffplay.exe are all next to vidslice.exe (or however that'll work on a Mac, hit me up if you have an explanation for this).
3. If you want to be able to download things, [download youtube-dl](https://rg3.github.io/youtube-dl/download.html) and put it in the same place as ffmpeg.

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
