from pathlib import Path
from typing import Any

from PySide6.QtCore import QRunnable, Slot, Signal, QObject
from ffmpeg import Progress

from tableUI.utils.assets.video.transcode import create_ffmpeg_instance_for_background_video_transcode

class BGVideoSignalSet(QObject):
    # Actual type is list[str]
    started = Signal(Any)
    progress = Signal(Any)
    completed = Signal()
    terminated = Signal()

    def __init__(self, parent: QObject = None):
        super().__init__(parent)

class BackgroundVideoTranscodeWorker(QRunnable):
    """
    Transcodes a video to be used as a song background, emitting signals based on its current status.
    All events from ``FFmpeg.execute()`` are pushed to Signals with equivalent names.
    """


    def __init__(self, input_path: Path, output_path: Path, quality: int = 1):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.quality = quality
        self.signals = BGVideoSignalSet()

    @Slot()
    def run(self):
        """Starts the video transcoding process."""
        ffmpeg = create_ffmpeg_instance_for_background_video_transcode(
            input_path=self.input_path,
            output_path=self.output_path,
            quality=self.quality
        )

        @ffmpeg.on('start')
        def on_start(args: list[str]):
            self.signals.started.emit((args,))

        @ffmpeg.on('progress')
        def on_progress(progress: Progress):
            self.signals.progress.emit(progress)

        @ffmpeg.on('completed')
        def on_completed():
            self.signals.completed.emit()

        @ffmpeg.on('terminated')
        def on_terminated():
            self.signals.terminated.emit()

        ffmpeg.execute()