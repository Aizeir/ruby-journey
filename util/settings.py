from pygame.math import Vector2 as vec2
from pygame.math import Vector3 as vec3
from util.keybinds import *

# General
W, H = 1280, 720
FPS = 120
ANIM_SPEED = 8
MUSIC_END = pg.USEREVENT+1

# Tiles
SCALE = 5
TILESIZE = TS = 16*SCALE
TILE = vec2(TILESIZE,TILESIZE)
TILEINT = (TILESIZE,TILESIZE)

# Minimap
MM = 4
MMSCALE = TS // MM

# Hitboxes (faire les autres!)
PLR_HITBOX =   (10*SCALE, 6*SCALE,    8*SCALE)
PNJ_HITBOX =   ( 7*SCALE, 4*SCALE,    4*SCALE)
QUEEN_HITBOX = (48*SCALE,24*SCALE,   20*SCALE)
ANIMAL_HITBOX = {
    'chicken': (12*SCALE, 5*SCALE,    4*SCALE),
    'racoon':  (12*SCALE, 5*SCALE,    4*SCALE)
}

SIDES = ["B","T","L","R"]

# Maps
WILD = 'wild'
MINES = 'mines'
DUNGEON = 'dungeon'
MAPS = (WILD,MINES,DUNGEON)
WILDCOLOR = "#5a8c6c"

# Hitbox
PROP_MARGIN = int(TS*.2)
BOAT_OFF = (7, -13)

# UI
TYPE_TIME = 50
UI_SCALE = 4
TITLE_BD = 4
UI = [
    (19,19,19),
    (38,38,38),
    (73,73,73),
    (118,118,118),
    (171,171,171),
    (203,203,203),
    (223,223,223),
    (244,244,244),
]

# Tools
TOOLS = {3:'axe',4:'pickaxe',5:'lance',8:'fish rod',13:'hammer',14:'slingshot',15:"watering can"}
TOOL_DURA = {3:60,4:36,5:36,8:36,13:24,14:-1,15:1}
TOOL_ATTACK = {
    3: (1, 1),
    4: (1.5, 1.5),
    5: (1, .75),
    13: (1.5, 2),
}
HAMMER_RANGE = TS*1.5

# Items
ITEMS = {
    'gold': "The world's currency.\nYou reached Golden Age.",
    'ruby': "You made it.\nYou got the ruby.",
    'rock': "A common material.\nYou reached Stone Age.",
    TOOLS[3]: "The cheapest tool.\nCollects wood.",
    TOOLS[4]: "Another tool.\nCollects stone.",
    TOOLS[5]: "A melee weapon.",
    'wood': "A basic material.\nEveryone starts somewhere.",
    'iron': "A very useful material.\nYou reached Iron Age.",
    TOOLS[8]: "Used for fishing.\nFisherman teaches it.",
    'fish': "A fish.",
    'meat': "Food from chickens.",
    "key": "Key to the mines.\nWhat's inside ?",
    "tail": "From mine animals.\nA corner shines.",
    TOOLS[13]: "Collects iron.\nWider range.",
    TOOLS[14]: "Shoot using stones.\nInfinite uses.",
    TOOLS[15]: "Water fruit trees.\nUse lakes to fill it.",
    "apple": "You can't eat it sorry.\nGrow in fruit trees.",
    "bronze": "The village's currency.\nYou reached Bronze Age.",
}
ITEMNAMES = list(ITEMS.keys())

# Other
FRUITTREE_TIME = 5