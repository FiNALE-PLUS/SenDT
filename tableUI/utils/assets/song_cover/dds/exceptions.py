class SongCoverError(ValueError):
    pass

class SongCoverSourceImageError(SongCoverError):
    pass

class SongCoverProcessingError(SongCoverError):
    pass