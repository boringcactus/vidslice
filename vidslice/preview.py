import subprocess
import tempfile
import threading
from tkinter import *
from tkinter import ttk

from options import FFmpegOptions


class PreviewPanel(ttk.LabelFrame):
    def __init__(self, *args, get_ffmpeg_args=lambda: FFmpegOptions([], []), get_frame_count=lambda: 0, **kw):
        super(PreviewPanel, self).__init__(*args, text='Preview', **kw)
        self.input_path = None
        self.get_ffmpeg_args = get_ffmpeg_args
        self.get_frame_count = get_frame_count

        def button(text, command, column):
            ttk.Button(self, text=text, command=command).grid(column=column, row=0, sticky=(N, W, S, E))
            self.columnconfigure(column, weight=1)

        button("Preview Start", self.preview_start, 0)
        button("Preview Middle", self.preview_middle, 1)
        button("Preview End", self.preview_end, 2)

        self.image = None
        self.image_label = ttk.Label(self, anchor='center')
        self.image_label.grid(column=0, row=1, columnspan=3, sticky=(N, W, S, E))
        self.rowconfigure(1, weight=1)

        self.enable(False)

    def preview_at(self, offset):
        offset = int(offset)
        self.enable(False)
        real_args = self.get_ffmpeg_args()
        input_args = real_args.input
        width = self.image_label.winfo_width()
        height = self.image_label.winfo_height()
        real_args.vf += [
            rf'select=eq(n\,{offset})',
            f'scale=w={width}:h={height}:force_original_aspect_ratio=decrease'
        ]
        real_args.output += ['-frames:v', '1']
        output_args = real_args.output_with_vf()

        def run():
            _, output_path = tempfile.mkstemp(suffix='.png')
            args = ['ffmpeg', '-hide_banner', '-v', 'warning', '-y'] + input_args + \
                   ['-i', self.input_path] + output_args + [output_path]
            print(args)
            # noinspection PyArgumentList
            proc = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            while proc.poll() is None:
                out_data = proc.stdout.readline()
                if out_data != '':
                    print(out_data, end='')
            self.enable(True)
            self.image = PhotoImage(file=output_path)
            self.image_label['image'] = self.image

        threading.Thread(target=run).start()

    def preview_start(self, *args):
        self.preview_at(0)

    def preview_middle(self, *args):
        self.preview_at(self.get_frame_count() / 2)

    def preview_end(self, *args):
        self.preview_at(self.get_frame_count() - 1)

    def enable(self, enabled):
        state = 'disabled'
        if enabled:
            state = '!' + state
        self.state([state])
        for child in self.winfo_children():
            try:
                child.state([state])
            except AttributeError:
                pass

    def set_input_path(self, path, data):
        self.enable(data is not None)
        if data is None:
            self.input_path = None
        else:
            self.input_path = path
