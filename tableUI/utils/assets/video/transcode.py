from pathlib import Path

from ffmpeg import FFmpeg, Progress

from tableUI.const import FFMPEG_PATH

KILOBYTE = 1024 * 1024


# TODO: add configuration and worker for UI
def create_ffmpeg_instance_for_background_video_transcode(input_path: Path, output_path: Path,
                                                          bitrate: int = 5 * KILOBYTE) -> FFmpeg:
    """
    Returns a ``FFmpeg`` instance preconfigured to transcode an input video
    to one suitable for Maimai FiNALE when ``execute`` is called.
    Videos that do not have an aspect ratio of 1:1 will have black bars added to fit within the play area without distortion.

    :param input_path: The path of the input video to transcode.
    :param output_path: The path of the output video to write to. Note that the file extension will be ``wmv``.
    :param bitrate: The bitrate of the output video. This defaults to 5kbps.
    :return: An ``FFmpeg`` instance that will transcode to the video at ``output_path``.
    """
    ffmpeg = (
        FFmpeg(executable=str(FFMPEG_PATH.absolute())).
        option('y').
        # option().
        # option('fps', 30).
        input(
            str(input_path.absolute()),
        ).
        output(
            str(output_path.with_suffix('.wmv').absolute()),
            {
                'vcodec': 'wmv2',
                'b:v': bitrate,
                # Forced 30 FPS
                'r': 30,
                # 1:1 aspect ratio
                'aspect': 1,
                # Resize to 600x600 with black bars
                'vf': r"scale=600:600:force_original_aspect_ratio=decrease, pad=600:600:(ow-iw)/2:(oh-ih)/2",
                # Remove audio tracks from output
                'an': None
            },
            # kwargs=('an',)
        )
    )

    return ffmpeg

if __name__ == '__main__':
    fmp = create_ffmpeg_instance_for_background_video_transcode(
        Path(r'C:\Users\sebas\Videos\4K Video Downloader+\[MV] TAK - ‘PPPP’ feat. Hatsune Miku, Kasane Teto.mp4'),
        Path(r'./transcoded.wmv')
    )

    

    @fmp.on('start')
    def on_start(arguments: list[str]):
        print("arguments:", arguments)

    @fmp.on('progress')
    def on_progress(progress: Progress):
        print(progress.time)


    @fmp.on("completed")
    def on_completed():
        print("completed")


    @fmp.on("terminated")
    def on_terminated():
        print("terminated")

    fmp.execute()