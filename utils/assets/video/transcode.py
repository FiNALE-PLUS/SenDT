from io import BytesIO
import json
from pathlib import Path
from warnings import deprecated

from ffmpeg import FFmpeg, Progress

from ffmpeg.asyncio import FFmpeg as AsyncFFmpeg

from const import FFMPEG_PATH, FFPROBE_PATH
from .mask import generate_finale_pv_mask


# TODO: add configuration and worker for UI
@deprecated('Phase out serverless GUI usage')
def create_ffmpeg_instance_for_background_video_transcode(input_path: Path, output_path: Path,
                                                          quality: int = 1) -> FFmpeg:
    """
    Returns a ``FFmpeg`` instance preconfigured to transcode an input video
    to one suitable for Maimai FiNALE when ``execute`` is called.
    Videos that do not have an aspect ratio of 1:1 will have black bars added to fit within the play area without distortion.

    :param input_path: The path of the input video to transcode.
    :param output_path: The path of the output video to write to. Note that the file extension will be ``wmv``.
    :param quality: The target video quality. Lower is higher quality and file size. Bitrate *is not* directly accessible via this function.
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
                # 'b:v': bitrate,
                # 'b:v': bitrate,
                'q:v': quality,
                # Forced 30 FPS - removed as Maimai has been found to use other (notably higher) framerate videos in some cases
                # 'r': 30,
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

async def transcode_bg_with_reflection(input_path: Path, output_path: Path,
                                                          quality: int = 1) -> FFmpeg:
    """
    Returns a ``FFmpeg`` instance preconfigured to transcode an input video
    to one suitable for Maimai FiNALE when ``execute`` is called.
    Videos that do not have an aspect ratio of 1:1 will have black bars added to fit within the play area without distortion.

    :param input_path: The path of the input video to transcode.
    :param output_path: The path of the output video to write to. Note that the file extension will be ``wmv``.
    :param quality: The target video quality. Lower is higher quality and file size. Bitrate *is not* directly accessible via this function.
    :return: An ``FFmpeg`` instance that will transcode to the video at ``output_path``.
    """
    
    ffprobe = (
        AsyncFFmpeg(executable=FFPROBE_PATH.absolute()).
        input(
            str(input_path.absolute()),
            ).
        option('print_format', 'json').
        option('show_streams', None)
        )
    
    media = json.loads(await ffprobe.execute())
    
    input_width, input_height = media['streams'][0]['width'], media['streams'][0]['height']
    
    # TODO: Replace with dynamic resolution based on input
    mask = generate_finale_pv_mask(input_width, input_height)
    
    mask_io = BytesIO()
    mask.save(mask_io, format='PNG')
    
    ffmpeg = (
        AsyncFFmpeg(executable=str(FFMPEG_PATH.absolute())).
        option('y').
        # option().
        # option('fps', 30).
        input(
            str(input_path.absolute()),
        ).
        # Used to add the mask without writing to disk
        input('pipe:0').
        output(
            str(output_path.with_suffix('.wmv').absolute()),
            {
                'vcodec': 'wmv2',
                # 'b:v': bitrate,
                # 'b:v': bitrate,
                'q:v': quality,
                # Forced 30 FPS - removed as Maimai has been found to use other (notably higher) framerate videos in some cases
                # 'r': 30,
                # 1:1 aspect ratio
                'aspect': 1,
                # Resize to 600x600 with black bars
                'filter_complex': 
                    r"[0:v]scale=600:600:force_original_aspect_ratio=decrease[cropped];"
                    r"[cropped] split [main][to_mirror];"
                    r"[main] pad=600:600:(ow-iw)/2:(oh-ih)/2 [centre];"
                    r"[to_mirror] vflip [mirror];"
                    r"[centre][mirror] overlay=0:(main_h/2)+(overlay_h/2)+2[stack];"
                    r"[stack]crop=600:600:0:0[cropped_stack];"
                    r"[1:v] alphaextract [alpha];"
                    r"[cropped_stack][alpha] alphamerge[stack_with_alpha];"
                    r"[stack_with_alpha] premultiply=inplace=yes",
                # Remove audio tracks from output
                'an': None
            },
            # kwargs=('an',)
        )
    )

    await ffmpeg.execute(mask_io.getvalue())