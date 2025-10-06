from tableUI.parsers.tables.field_types.quoted_string import DoubleQuotedString


def safename_from_song_name(name: str, song_id: int) -> DoubleQuotedString:
    valid_chars = ''.join(char.lower() for char in name if (char.isalnum() and char.isascii()) or char == ' ')[:17]

    safename = ''

    for char in valid_chars:
        if char == ' ':
            safename += '_'
        else:
            safename += char

    safename = safename.strip('_')

    if safename == '':
        safename = f'song_{song_id}'
    else:
        safename = f'{safename}_{song_id}'

    return DoubleQuotedString(safename)
