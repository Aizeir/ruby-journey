import sys, os
import pygame as pg

def res(relpath):
    return relpath

 
def sound(path, vol=.4):
    s = pg.mixer.Sound(res("assets/sounds/"+path))
    s.set_volume(vol)
    return s

walk = [sound("walk/"+file, .7) for file in os.listdir('assets/sounds/walk')]
walk_mines = [sound("walkmines/"+file, 1) for file in os.listdir('assets/sounds/walkmines')]
mines_enter = sound("mines.wav", .7)
mines_exit = sound("mines_out.wav", .7)
ladder = sound("ladder.wav", 10)
stair = sound("stair.wav", 10)
boat = sound("boat.wav", .5)

click = sound("click.wav", 1)
press = sound("press.wav", 10)
release = sound("press.wav", 10)
pause = sound("pause.wav", 1)
talk = sound("talk.wav", .8)
ptalk = sound("paneltalk.wav", .5)
dclick = sound("dialogclick.wav", .3)
friend = sound("friend.wav", 1)
switch = sound("switch.wav", 10)
hover = sound("hover.wav", 1)
panel = sound("panel.wav", 1)
quest = sound("quest.wav", 1)

hammer = sound("hammer.wav", .4)
sword = sound("sword.wav", .5)
axe = sound("axe.wav", .2)
pickaxe = sound("pickaxe.wav", 10)
water = sound("water.wav", 1)
collect = sound("collect.wav")
broken = sound("broken.wav", 1)
hit = sound("hit.wav", 10)
lasthit = sound("lasthit.wav", 1)

bubbles = sound("bubbles.wav", 1)
fishing = sound("fishing.wav", .5)
fish = sound("fish.wav", 1)

hurt = sound("hurt.wav", 1)
dead = sound("dead.wav", 10)
plrhurt = sound("plrhurt.wav", 1)
plrdead = sound("plrdead.wav", 1)
hurtqueen = sound("hurtqueen.wav")
deadqueen = sound("deadqueen.wav", 10)
yes = sound("yes.wav", 10)

slingshot = sound("slingshot.wav", 1)
stone = sound("stone.wav", 1)

ambiance = sound("ambiance.wav", .5)
crickets = sound("crickets.wav", .5)
wind = sound("wind.wav", .5)