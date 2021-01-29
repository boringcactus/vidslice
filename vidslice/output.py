import os
import subprocess
import threading
from tkinter import *
from tkinter import filedialog
from tkinter import ttk

from options import FFmpegOptions


class OutputPanel(ttk.LabelFrame):
    def __init__(self, *args, get_ffmpeg_args=lambda: FFmpegOptions([], [], []), get_frame_count=lambda: 0, **kw):
        super(OutputPanel, self).__init__(*args, text='Output', **kw)
        self.update_listeners = []
        self.input_path = None
        self.get_ffmpeg_args = get_ffmpeg_args
        self.get_frame_count = get_frame_count

        ttk.Label(self, text="File").grid(column=0, row=0, sticky=W)
        self.file_text = StringVar(self)
        ttk.Entry(self, textvariable=self.file_text, width=30).grid(column=1, row=0, columnspan=2, sticky=(E, W))
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.file_text.trace_add("write", self.handle_file_changed)
        ttk.Button(self, text="Browse", command=self.handle_file_browse_pressed).grid(column=3, row=0, sticky=E)

        self.silence = BooleanVar(self)
        ttk.Checkbutton(self, text="Silence", variable=self.silence, onvalue=True, offvalue=False
                        ).grid(column=0, row=1, columnspan=2, sticky=W)
        self.deepfry = BooleanVar(self)
        ttk.Checkbutton(self, text="Compress beyond recognition", variable=self.deepfry, onvalue=True, offvalue=False
                        ).grid(column=2, row=1, columnspan=2, sticky=W)

        run_button = ttk.Button(self, text="Run", command=self.handle_run_pressed)
        run_button.grid(column=0, row=2, sticky=(E, W))
        run_preview_button = ttk.Button(self, text="Run & Preview", command=self.handle_run_preview_pressed)
        run_preview_button.grid(column=1, row=2, columnspan=2, sticky=(E, W))
        run_quit_button = ttk.Button(self, text="Run & Quit", command=self.handle_run_quit_pressed)
        run_quit_button.grid(column=3, row=2, sticky=(E, W))

        self.progress = ttk.Progressbar(self, orient=HORIZONTAL, mode='determinate')
        self.progress.grid(column=0, row=3, columnspan=4, sticky=(N, S, E, W))

        self.logs = StringVar(self)
        logs_widget = ttk.Label(self, textvariable=self.logs, font="TkFixedFont",
                                justify='left')
        logs_widget.grid(column=0, row=4, columnspan=4, sticky=(N, S, E, W))
        self.rowconfigure(4, weight=1)

        for child in self.winfo_children():
            child.grid_configure(padx=2, pady=2)

        self.enable(False)

    def enable(self, enabled, run_enabled=None):
        if run_enabled is None:
            run_enabled = enabled
        state = 'disabled'
        if enabled:
            state = '!' + state
        run_state = 'disabled'
        if run_enabled:
            run_state = '!' + run_state
        self.state([state])
        for child in self.winfo_children():
            if 'text' in child.configure() and child['text'].startswith('Run'):
                child.state([run_state])
            else:
                child.state([state])

    def handle_file_changed(self, *args):
        path = self.file_text.get()
        (folder, name) = os.path.split(path)
        try:
            os.stat(folder)
            self.enable(True)
        except FileNotFoundError:
            self.enable(True, False)

    def handle_file_browse_pressed(self, *args):
        filename = filedialog.asksaveasfilename(parent=self)
        if filename != '':
            self.file_text.set(filename)

    def handle_run_pressed(self, *args, callback=lambda _: None):
        self.logs.set('')
        self.progress['value'] = 0
        self.enable(False)
        real_args = self.get_ffmpeg_args()
        self.progress['maximum'] = float(self.get_frame_count())
        print(self.get_frame_count())
        input_args = real_args.input
        output_args = real_args.output_with_vf()
        output_path = self.file_text.get()
        (folder, name) = os.path.split(output_path)
        (name, ext) = os.path.splitext(name)
        if self.silence.get():
            output_args += ['-an']
        if ext == '.gif':
            filter_before = '[0:v] '
            filter_after = 'split [a][b];[a] palettegen [p];[b][p] paletteuse'
            filter_during = ''
            if '-vf' in output_args:
                for i in range(len(output_args) - 1):
                    [a, b] = output_args[i:i + 2]
                    if a == '-vf':
                        filter_during = b + ','
                    output_args[i:i + 2] = []
                    break
            output_args += ['-filter_complex', filter_before + filter_during + filter_after]
        if self.deepfry.get():
            if ext == '.mp3':
                output_args += ['-q:a', '9']
            else:
                output_args += ['-q:a', '0.1', '-crf', '51']
        args = ['ffmpeg', '-hide_banner', '-v', 'warning', '-stats', '-y'] + input_args + ['-i',
                                                                                           self.input_path] + output_args + [
                   output_path]
        print(args)

        def run():
            # noinspection PyArgumentList
            proc = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            while proc.poll() is None:
                out_data = proc.stdout.readline()
                if out_data != '':
                    progress_data = re.match(r'^frame=\s*(\d+)', out_data)
                    print(out_data, end='')
                    if progress_data is not None:
                        self.progress['value'] = float(progress_data.group(1))
                    else:
                        self.logs.set(self.logs.get() + out_data)
            self.progress['value'] = self.progress['maximum']
            self.enable(True)
            callback(proc.returncode)

        threading.Thread(target=run).start()

    def handle_run_preview_pressed(self, *args):
        def preview(code):
            if code == 0:
                out_file = self.file_text.get()
                subprocess.Popen(['ffplay', '-autoexit', out_file], creationflags=subprocess.CREATE_NO_WINDOW)

        self.handle_run_pressed(*args, callback=preview)

    def handle_run_quit_pressed(self, *args):
        def quit(code):
            if code == 0:
                toplevel = self.winfo_toplevel()
                toplevel.destroy()

        self.handle_run_pressed(*args, callback=quit)

    def set_input_path(self, path, data):
        if data is None:
            self.enable(False)
            self.input_path = None
        else:
            self.handle_file_changed()
            self.input_path = path
