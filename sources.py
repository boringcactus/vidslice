import glob
import json
import os
import subprocess
import tempfile
import threading
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk


def has_ytdl():
    try:
        subprocess.run(["youtube-dl", "--version"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except FileNotFoundError:
        return False


def update_ytdl(root):
    try:
        youtube_dl_found = subprocess.run(['where', 'youtube-dl'], stdout=subprocess.PIPE, text=True,
                                          creationflags=subprocess.CREATE_NO_WINDOW)
    except FileNotFoundError:
        youtube_dl_found = subprocess.run(['which', 'youtube-dl'], stdout=subprocess.PIPE, text=True,
                                          creationflags=subprocess.CREATE_NO_WINDOW)
    if youtube_dl_found.returncode != 0:
        answer = messagebox.askyesno(message="Could not find youtube-dl. Open vidslice README?", title="Error",
                                     icon='error', parent=root)
        if answer:
            import webbrowser
            webbrowser.open("https://github.com/boringcactus/vidslice/blob/master/README.md")
    youtube_dl_path = youtube_dl_found.stdout.split("\n")[0]
    old_mtime = os.stat(youtube_dl_path).st_mtime
    proc = subprocess.run(["youtube-dl", "-U"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                          creationflags=subprocess.CREATE_NO_WINDOW)
    if not proc.stdout.startswith("youtube-dl is up-to-date") and not proc.stdout.startswith("ERROR"):
        while os.stat(youtube_dl_path).st_mtime == old_mtime:
            from time import sleep
            sleep(0.25)
    messagebox.showinfo(message="Updated youtube-dl successfully", title="Complete", parent=root)


class SourcesPanel(ttk.LabelFrame):
    """
    A Panel representing source info
    """

    def __init__(self, *args, **kw):
        super(SourcesPanel, self).__init__(*args, text='Sources', **kw)
        self.update_listeners = []

        if has_ytdl():
            ttk.Label(self, text="URL").grid(column=0, row=0, sticky=(E, W))
            self.url_text = StringVar(self)
            ttk.Entry(self, textvariable=self.url_text).grid(column=1, row=0, sticky=(E, W))
            ttk.Button(self, text="Download", command=self.handle_url_download_pressed
                       ).grid(column=2, row=0, sticky=(E, W))
        else:
            ttk.Label(self, text="Could not find youtube-dl, can't download videos automatically"
                      ).grid(column=0, row=0, columnspan=3, sticky=(E, W))
            self.url_text = None

        ttk.Label(self, text="File").grid(column=0, row=1, sticky=(E, W))
        self.file_text = StringVar(self)
        self.file_text.trace_add("write", self.handle_file_changed)
        ttk.Entry(self, textvariable=self.file_text).grid(column=1, row=1, sticky=(E, W))
        self.columnconfigure(1, weight=1)
        ttk.Button(self, text="Browse", command=self.handle_file_browse_pressed).grid(column=2, row=1, sticky=(E, W))

        self.status_label = StringVar(self, "Status: Select a file")
        ttk.Label(self, textvariable=self.status_label).grid(column=0, row=2, columnspan=3, sticky=(E, W))

        for child in self.winfo_children():
            child.grid_configure(padx=2, pady=2)

    def set_status(self, text):
        self.status_label.set("Status: " + text)

    def handle_url_download_pressed(self, *args):
        self.set_status("Downloading...")

        def download():
            file = tempfile.NamedTemporaryFile(delete=False)
            # noinspection PyArgumentList
            proc = subprocess.Popen([
                'youtube-dl', '-o', file.name + '.%(ext)s', self.url_text.get()
            ], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW)
            while proc.poll() is None:
                out_data = proc.stdout.readline()
                if out_data != '':
                    self.set_status("Downloading: " + out_data.strip())
            if proc.returncode == 0:
                output_file = glob.glob(glob.escape(file.name) + '.*')[0]
                self.set_status("Downloaded!")
                self.file_text.set(output_file)
            else:
                error = ''.join(proc.stderr.readlines()).strip()
                self.set_status("Couldn't download: " + error)

        threading.Thread(target=download).start()

    def handle_file_browse_pressed(self, *args):
        filename = filedialog.askopenfilename(parent=self)
        if filename != '':
            self.file_text.set(filename)

    def handle_file_changed(self, *args):
        def probe():
            result = subprocess.run([
                'ffprobe', '-v', 'error', '-of', 'json',
                '-show_entries', 'format=start_time,duration:stream=index,codec_type,avg_frame_rate,width,height',
                self.file_text.get()
            ], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode == 0:
                ffprobe_data = json.loads(result.stdout)
                self.set_status("Successfully loaded media info")
                for listener in self.update_listeners:
                    listener(ffprobe_data)
            else:
                self.set_status("Failed to load media info: " + result.stderr)
                for listener in self.update_listeners:
                    listener(None)

        threading.Thread(target=probe).start()

    def on_update(self, callback):
        self.update_listeners.append(callback)

    def get_file(self):
        return self.file_text.get()
