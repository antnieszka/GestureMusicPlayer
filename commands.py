from subprocess import check_call

__all__ = ['play', 'pause', 'move_prev', 'move_next', 'vol_up', 'vol_down']


def play():
    check_call(['vlc-ctrl', 'play'])


def pause():
    check_call(['vlc-ctrl', 'pause'])


def move_next():
    check_call(['vlc-ctrl', 'next'])


def move_prev():
    check_call(['vlc-ctrl', 'prev'])


def vol_up():
    check_call(['vlc-ctrl', 'volume', '+0.1'])


def vol_down():
    check_call(['vlc-ctrl', 'volume', '-0.1'])
