from util import *

# Shadow constants - hitbox: (w,h, shadow height)
SHS = 4*SCALE
SHB = 10*SCALE

PROP_DATA = {
    "campfire": {
        "hitbox":(10*SCALE,10*SCALE),
        'small':1,
    },

    "house": {
        "hitbox":(38*SCALE,21*SCALE,  7*SCALE),
    },
    "abandoned": {
        "damage":[0],
        "drop":(6, 16),
        "health":50,
        "hitbox":(58*SCALE,56*SCALE,  SHB),
        "tool":3,
        "mm": 11,
    },
    "tent": {
        "hitbox":(39*SCALE,30*SCALE,  SHB),
    },

    "mine": {
        "teleport": "ladder",
        "hitbox":(36*SCALE,21*SCALE,  SHB),
        "mm": 9,
    },
    "ladder": {
        "teleport": "mine",
        "hitbox":(13*SCALE,3*SCALE),
        "mm": 7,
    },
    "ladder2": {
        "teleport": "hole",
        "hitbox":(13*SCALE,3*SCALE),
    },
    "stair": {
        "teleport": "stair2",
        "hitbox":(14*SCALE,14*SCALE),
        "mm": 6,
    },
    "stair2": {
        "teleport": "stair",
        "hitbox":(14*SCALE,11*SCALE,  SHS),
        "mm": 6,
    },
    "hole": {
        "teleport": "ladder2",
        "hitbox":(32*SCALE,32*SCALE),
        'small':1,
        "mm": 7,
    },

    "stone": {
        "damage":[1],
        "drop":(2,2),
        "health":2,
        "hitbox":(9*SCALE,6*SCALE,  SHS),
        "tool":4,
        'small':1,
    },
    "iron": {
        "damage":[1,2],
        "drop":(7,1),
        "health":6,
        "hitbox":(9*SCALE,6*SCALE,  SHS),
        "tool":13,
        'small':1,
    },
    "stone_2": {
        "damage":[1],
        "drop":(2,4),
        "health":4,
        "hitbox":(13*SCALE,8*SCALE,  SHS),
        "tool":4,
        'small':1,
    },
    "stone_big": {
        "tool":4,
        "drop":(2,8),
        "health":8,
        "damage":[1],
        "hitbox":(20*SCALE,10*SCALE,  SHS),
    },

    "tree": {
        "damage":[0,3],
        "drop":(6,3),
        "health":3,
        "hitbox":(9*SCALE,9*SCALE,  SHB),
        "tool":3,
    },
    "tree2": {
        "damage":[0,3],
        "drop":(6,3),
        "health":3,
        "hitbox":(9*SCALE,9*SCALE,  SHB),
        "tool":3,
    },
    "fruit_tree": {
        "hitbox":(9*SCALE,9*SCALE,  SHB),
        "mm": 13,
    },
    "trunk": {
        "damage":[0],
        "drop":(6,6),
        "health":4,
        "hitbox":(13*SCALE,26*SCALE,  SHS),
        "tool":3,
    },
    "wood": {
        "damage":[0],
        "drop":(6,3),
        "health":2,
        "hitbox":(13*SCALE,10*SCALE,  SHS),
        "tool":3,
    },

    "torch": {
        "hitbox":(3*SCALE,3*SCALE),
        'small':1,
    },
    "boat":  {
        "hitbox":(52*SCALE,24*SCALE),
        "mm": 10,
    },
    "boatpnj":  {"hitbox":(52*SCALE,24*SCALE)},
    "boatpnj2": {"hitbox":(52*SCALE,24*SCALE)},
    "boatminer":{"hitbox":(52*SCALE,24*SCALE)},
}