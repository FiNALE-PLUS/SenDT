from pathlib import Path

from ffmpeg import FFmpeg

from tableUI.const import FFMPEG_PATH

KILOBYTE = 1024 * 1024


# TODO: add configuration and worker for UI
def convert_video_to_maimai_background(input_path: Path, output_path: Path):
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
                'b:v': 5 * KILOBYTE,
                # Forced 30 FPS
                'r': 30,
                # 1:1 aspect ratio
                'aspect': 1,
                # Resize to 600x600 with black bars
                'vf': r"scale=600:600:force_original_aspect_ratio=decrease, pad=600:600:(ow-iw)/2:(oh-ih)/2",
                'an': None
            },
            # kwargs=('an',)
        )
    )

    ffmpeg.execute()

