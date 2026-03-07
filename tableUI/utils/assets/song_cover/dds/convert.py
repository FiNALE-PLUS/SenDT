from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from PIL.Image import Resampling, Image as ImageObject

from const import BASE_DIR
from tableUI.utils.assets.song_cover.dds.exceptions import SongCoverSourceImageError, SongCoverProcessingError

SONG_COVER_FULL_SIZE = (256, 256)
SONG_COVER_RELFECTION_BASE_SIZE = (220, 220)
SONG_COVER_SMALL_SIZE = (128, 128)

# TODO: Use dataclass to allow for validation?

# class SongCoverImages(NamedTuple):
#     full_size: ImageObject
#     reflection_size: ImageObject
#     small: ImageObject


@dataclass
class SongCoverImageSet:
    full_size: ImageObject
    mirror_effect: ImageObject
    small: ImageObject

    def __post_init__(self):
        """
        Asserts basic sanity checks to ensure that cover images are of the correct dimensions.
        """
        assert self.full_size.size == SONG_COVER_FULL_SIZE
        assert self.full_size.mode == 'RGB'
        assert self.mirror_effect.size == SONG_COVER_FULL_SIZE
        assert self.mirror_effect.mode == 'RGBA'
        assert self.small.size == SONG_COVER_SMALL_SIZE
        assert self.small.mode == 'RGB'


def get_song_cover_texture_images_from(image: ImageObject):

    if image.width != image.height:
        raise SongCoverSourceImageError(f'The aspect ratio of the input image must be 1. (Image size is {image.size})')

    full_size_cover_texture = image.resize(SONG_COVER_FULL_SIZE, Resampling.LANCZOS).convert('RGB')
    small_cover_texture = image.resize(SONG_COVER_SMALL_SIZE, Resampling.LANCZOS).convert('RGB')

    mirror_effect_base_image = image.resize(SONG_COVER_RELFECTION_BASE_SIZE, Resampling.LANCZOS)
    mirror_effect_cover_texture = apply_mirror_effect_to_reflection_image(mirror_effect_base_image)

    return SongCoverImageSet(
        full_size=full_size_cover_texture,
        mirror_effect=mirror_effect_cover_texture,
        small=small_cover_texture,
    )


def get_reflection_image_from_base(base_image: ImageObject):
    if base_image.size != SONG_COVER_RELFECTION_BASE_SIZE:
        raise SongCoverSourceImageError(f'Base image for reflection image must be {SONG_COVER_RELFECTION_BASE_SIZE} (got {base_image.size})')


def convert_image_to_uncompressed_dds(path: Path):
    img = Image.open(path)

    img.save((path.parent / 'dxt5_mk').with_suffix('.dds'))


def extract_image_alpha_channel(image: ImageObject) -> ImageObject:
    # Guarantee alpha channel is separated
    img = image.convert('RGBA')
    alpha = img.split()[-1]
    # Create a new image with an opaque black background
    bg = Image.new("RGBA", img.size, (0, 0, 0, 255))

    # Copy the alpha channel to the new image using itself as the mask
    bg.paste(alpha, mask=alpha)
    return bg.convert('L')


def apply_mirror_alpha_channel(image: ImageObject):
    if image.size != SONG_COVER_FULL_SIZE:
        raise SongCoverProcessingError(f'The size of the input image must be {SONG_COVER_FULL_SIZE} (got {image.size})')

    img_with_alpha = image.convert('RGBA')
    img_with_alpha.putalpha(Image.open(BASE_DIR / 'data' / 'img' / 'song_cover' / 'mirror_alpha.png'))

    return img_with_alpha

def apply_mirror_effect_to_reflection_image(image: ImageObject):
    if image.size != SONG_COVER_RELFECTION_BASE_SIZE:
        raise SongCoverProcessingError(f'The size of the image to apply effects to '
                                       f'must be {SONG_COVER_RELFECTION_BASE_SIZE} (got {image.size})')
    final_cover = Image.new('RGBA', SONG_COVER_FULL_SIZE, (0, 0, 0, 0))
    final_cover.paste(image, (18, 0))
    flipped_img = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    final_cover.paste(flipped_img, (18, 222))
    return apply_mirror_alpha_channel(final_cover)


def save_cover_textures_from_image(image: ImageObject, output_dir: Path):
    assert output_dir.is_dir(), output_dir.exists()

    cover_textures = get_song_cover_texture_images_from(image)

    cover_textures.small.save(output_dir / 'small.dds')
    cover_textures.full_size.save(output_dir / 'full.dds')
    cover_textures.mirror_effect.save(output_dir / 'mirror.dds')
