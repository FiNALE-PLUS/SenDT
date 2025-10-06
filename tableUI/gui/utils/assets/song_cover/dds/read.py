from PIL import Image
from PIL.Image import Image as ImageObject

from tableUI.const import FULL_COVER_ART_NAME, MIRROR_COVER_ART_NAME, SMALL_COVER_ART_NAME
from tableUI.gui.utils.assets.song_cover.dds.convert import SongCoverImageSet
from tableUI.paths import get_user_data_cover_art_dir_for


# TODO: Refactor user data to reside within single folder (user -> `id` over `id` within multiple dirs)
#  Add changed dir to song removal

def open_cover_art_images_for_song_id(song_id: int) -> SongCoverImageSet:
    cover_art_dir = get_user_data_cover_art_dir_for(song_id)

    if not cover_art_dir.exists():
        raise FileNotFoundError(f'Cover art directory {cover_art_dir} does not exist')

    missing_files = []

    full_size_img_path = cover_art_dir / FULL_COVER_ART_NAME
    mirror_img_path = cover_art_dir / MIRROR_COVER_ART_NAME
    small_size_img_path = cover_art_dir / SMALL_COVER_ART_NAME

    for path in (full_size_img_path, mirror_img_path, small_size_img_path):
        if not path.exists():
            missing_files.append(path)

    if missing_files:
        raise FileNotFoundError(f'Cover art images for song {song_id} does not exist. '
                                f'Couldn\'t find:\n\t{'\n\t'.join(str(path.absolute()) for path in missing_files)}')

    return SongCoverImageSet(
        full_size=Image.open(full_size_img_path),
        mirror_effect=Image.open(mirror_img_path),
        small=Image.open(small_size_img_path))
