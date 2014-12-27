"""
This module initializes the display and creates dictionaries of resources.
"""
import os
import pygame as pg
from . import tools
from . import events


ORIGINAL_CAPTION = "Py Rollers Casino"
START_SIZE = (928, 696)
RENDER_SIZE = (1400, 1050)
RESOLUTIONS = [(600,400),(800, 600), (928, 696), (1280, 960), (1400, 1050)]
CARD_SIZE = (125, 181)
CHIP_SIZE = (32, 19)
WIN_POS = (0,0)
MONEY = 999
ARGS = tools.get_cli_args(ORIGINAL_CAPTION, WIN_POS, START_SIZE, MONEY)
#adjust settings based on args
START_SIZE = int(ARGS['size'][0]), int(ARGS['size'][1])
MONEY = int(ARGS['money'])
DEBUG = bool(ARGS['debug'])

#Pre-initialize the mixer for less delay before a sound plays
pg.mixer.pre_init(44100, -16, 1, 512)

#Initialization
pg.init()
if ARGS['center']:
    os.environ['SDL_VIDEO_CENTERED'] = "True"
else:
    os.environ['SDL_VIDEO_WINDOW_POS'] = '{},{}'.format(ARGS['winpos'][0], ARGS['winpos'][1])
pg.display.set_caption(ORIGINAL_CAPTION)
if ARGS['fullscreen']:
    pg.display.set_mode(START_SIZE, pg.FULLSCREEN)
else:
    pg.display.set_mode(START_SIZE, pg.RESIZABLE)
    pg.event.clear(pg.VIDEORESIZE)


#Resource loading (Fonts and music just contain path names).
FONTS = tools.load_all_fonts(os.path.join("resources", "fonts"))
MUSIC = tools.load_all_music(os.path.join("resources", "music"))
SFX   = tools.load_all_sfx(os.path.join("resources", "sound"))
GFX   = tools.load_all_gfx(os.path.join("resources", "graphics"))

#strip cards from sheet and add to GFX individually
card_width = 125
card_height = 181
sheet = GFX["cardsheet"]
card_names = ["ace"]
card_names.extend(list(range(2, 11)))
card_names.extend(["jack", "queen", "king"])
top = 0
for suit in ["clubs", "hearts", "diamonds", "spades"]:
    left = 0
    for name in card_names:
        rect = pg.Rect(left, top, card_width, card_height)
        key = "{}_of_{}".format(name, suit)
        GFX[key] = sheet.subsurface(rect)
        left += card_width
    top += card_height



#It's time to start the music, it's time to light the lights
pg.mixer.music.load(MUSIC["main_stem"])
pg.mixer.music.set_volume(.2)
if not ARGS["music_off"]:
    pg.mixer.music.play()

# Singleton to broadcast events throughout the game
BROADCASTER = events.Broadcaster()