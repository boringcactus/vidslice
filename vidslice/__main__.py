import json
import subprocess
import sys
import urllib.request
from tkinter import *
from tkinter import messagebox
from tkinter import ttk

from options import OptionsPanel
from output import OutputPanel
from preview import PreviewPanel
from sources import SourcesPanel, update_ytdl

VERSION = "1.6"


def check_update(parent):
    latest_release_api_url = 'https://api.github.com/repos/boringcactus/vidslice/releases/latest'
    with urllib.request.urlopen(latest_release_api_url) as latest_release_response:
        latest_release_obj = json.load(latest_release_response)
    newest_version = latest_release_obj['tag_name'].lstrip('v')
    if VERSION != newest_version:
        open_update = messagebox.askyesno(message="vidslice update available. download?", title="Update",
                                          parent=parent)
        if open_update:
            import webbrowser

            webbrowser.open("https://github.com/boringcactus/vidslice/releases/latest")


def has_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except FileNotFoundError:
        return False


class VidsliceFrame:
    def __init__(self, root: Tk):
        self.root = root
        root.title('vidslice')

        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.sources_panel = SourcesPanel(mainframe)
        self.sources_panel.grid(column=0, row=0, columnspan=2, sticky=(W, E, N, S), padx=5, pady=5)

        self.options_panel = OptionsPanel(mainframe)
        self.options_panel.grid(column=0, row=1, columnspan=2, sticky=(W, N, S), padx=5, pady=5)
        self.sources_panel.on_update(self.options_panel.update_info)

        self.preview_panel = PreviewPanel(mainframe, get_ffmpeg_args=self.options_panel.ffmpeg_opts,
                                          get_frame_count=self.options_panel.frame_count)
        self.preview_panel.grid(column=0, row=2, sticky=(W, E, N, S), padx=5, pady=5)
        mainframe.rowconfigure(2, weight=1)
        mainframe.columnconfigure(0, weight=2)
        self.sources_panel.on_update(
            lambda data: self.preview_panel.set_input_path(self.sources_panel.get_file(), data))

        self.output_panel = OutputPanel(mainframe, get_ffmpeg_args=self.options_panel.ffmpeg_opts,
                                        get_frame_count=self.options_panel.frame_count)
        self.output_panel.grid(column=1, row=2, sticky=(W, E, N, S), padx=5, pady=5)
        mainframe.columnconfigure(1, weight=1)
        self.sources_panel.on_update(lambda data: self.output_panel.set_input_path(self.sources_panel.get_file(), data))

        # create a menu bar
        self.make_menu_bar(root)

        if len(sys.argv) > 1:
            self.sources_panel.file_text.SetValue(sys.argv[1])

    def make_menu_bar(self, root):
        root.option_add('*tearOff', FALSE)

        menubar = Menu(root)
        root['menu'] = menubar

        file_menu = Menu(menubar)
        menubar.add_cascade(menu=file_menu, label='File', underline=0)
        file_menu.add_command(label="Update youtube-dl", command=self.on_update, underline=0)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.on_exit, underline=1)

        help_menu = Menu(menubar)
        menubar.add_cascade(menu=help_menu, label='Help', underline=0)
        help_menu.add_command(label='About', command=self.on_about, underline=0)

    def on_exit(self, *args):
        self.root.destroy()

    def on_update(self, *args):
        import threading
        threading.Thread(target=update_ytdl, args=(self.root,)).start()

    def on_about(self, *args):
        messagebox.showinfo(message=f"vidslice {VERSION}")


def check_ffmpeg(root: Tk):
    if not has_ffmpeg():
        open_readme = messagebox.askyesno(message="Could not find ffmpeg. Open vidslice README?", title="Error",
                                          icon='error', parent=root)
        if open_readme:
            import webbrowser

            webbrowser.open("https://github.com/boringcactus/vidslice/blob/master/README.md")
            root.after(1000, root.destroy)


def main():
    root = Tk()
    frame = VidsliceFrame(root)
    root.after_idle(check_ffmpeg, root)
    root.after(1000, check_update, root)
    root.mainloop()


if __name__ == '__main__':
    main()
