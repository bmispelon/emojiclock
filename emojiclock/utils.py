import datetime
import unicodedata

ENGLISH_NUMBERS = ['twelve', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven']

_TIME_TO_EMOJI = {}
for i, number in enumerate(ENGLISH_NUMBERS):
    _TIME_TO_EMOJI[datetime.time(hour=i, minute=0)] = unicodedata.lookup('CLOCK FACE {} OCLOCK'.format(number))
    _TIME_TO_EMOJI[datetime.time(hour=i, minute=30)] = unicodedata.lookup('CLOCK FACE {}-THIRTY'.format(number))


_EMOJI_TO_TIME = {v: k for k, v in _TIME_TO_EMOJI.items()}


def round_to_nearest_half_hour(time):
    """
    Given a time object, return another time object corresponding to the
    nearest half hour time.
    """
    total_seconds = sum((
        (time.hour % 12) * 3600,
        time.minute * 60,
        time.second,
        time.microsecond * 10**-6
    ))

    total_half_hour_blocks = round(total_seconds/(30*60))

    return datetime.time(
        hour=total_half_hour_blocks // 2,
        minute=30 * (total_half_hour_blocks % 2)
    )


def time_to_emoji(time):
    """
    Return the (best possible) emoji representation of the given time.
    """
    rounded = round_to_nearest_half_hour(time)
    return _TIME_TO_EMOJI[rounded]


def emoji_to_time(emoji):
    """
    Return the time object corresponding to the given clock emoji.
    """
    return _EMOJI_TO_TIME[emoji]
