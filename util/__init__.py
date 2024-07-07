import pygame as pg
pg.init()
import os, time, sys, json, moderngl
from random import randint, shuffle, choice

import util.sounds as sounds
from util.keybinds import *
from util.settings import *
from util.timer import *

# Pyinstaller
def res(relpath):
    return relpath

# Debug
debug_font = pg.font.Font(None,30)
def debug(info, y=16, x=16, surf=None, font=debug_font):
    surf = surf or pg.display.get_surface()
    debug_surf = font.render(str(info),True,"white")
    debug_rect = debug_surf.get_rect(topleft = (x,y))
    pg.draw.rect(surf, UI[0], debug_rect.inflate(4, -6))
    surf.blit(debug_surf, debug_rect)

def screenshot(display, name=None):
    pg.image.save(display, name or f"capture{pg.time.get_ticks()}.png")

# Text
def font(path, size):
    return pg.font.Font(res("assets/ui/"+path), size)
# Text
def textr(text, font, color, **k):
    t = font.render(text, False, color)
    return t, t.get_rect(**k)
# Input
def iskeys(keys, K):
    return any([keys[k] for k in K])
# Random
def proba(x): return randint(1,x)==1
# Math
def clamp(m, x, M=None):
    if M != None: return max(m,min(x,M))
    else: return min(m, x)
# Thread
from threading import Thread
def thread(func):
    def inner(*a,daemon=True,**k):
        th = Thread(target=func, args=a, kwargs=k, daemon=daemon)
        th.start()
        return th
    return inner
# Music
def music(path, loops=1, vol=1, start=0, fade_ms=0):
    pg.mixer.music.load("assets/sounds/"+path)
    pg.mixer.music.set_volume(vol)
    pg.mixer.music.play(loops, start, fade_ms)

# Image
def load(image, scale=0, size=None):
    if isinstance(image, str):
        image = pg.image.load(res("assets/"+image+".png")).convert_alpha()
    if scale:
        size = vec2(image.get_size())*scale
    if size:
        image = pg.transform.scale(image, size)
    return image

def flips(images, x=0, y=0):
    return tuple(pg.transform.flip(i,x,y) for i in images)

def load_folder(path, scale=SCALE):
    images = []
    for _, _, files in os.walk(res("assets/"+path)):
        for filename in files:
            images.append(load(f"{path}/{filename.split(".")[0]}", scale))
    return images

def load_folder_dict(path, scale=SCALE):
    image_dict = {}
    for _, _, files in os.walk(res("assets/"+path)):
        for filename in files:
            name = filename.split(".")[0]
            image_dict[name] = load(f"{path}/{name}", scale)
    return image_dict

## MODIF LOAD TILESET !!
def load_tileset(path, size=(TS,TS), scale=SCALE):
    #size = (size[0]*scale,size[1]*scale)
    image = load(path, scale)
    tilemap = []
    
    for y in range(image.get_height()//size[1]):
        for x in range(image.get_width()//size[0]):
            tilemap.append(image.subsurface((x*size[0], y*size[1], size[0], size[1])))
    return tilemap

# outline (ui)
def ui_outline(overlay, img, color=UI[1], corner=False, big=True, **k):
    if isinstance(img, str):
        img, rect = textr(img, (overlay.font, overlay.fontbig)[big], UI[6], **k)
    else:
        img, rect = img, img.get_rect(**k)
        
    border = pg.mask.from_surface(img).to_surface(unsetcolor=(0,0,0,0),setcolor=color)
    for off in ((-1,0),(1,0),(0,-1),(0,1)):
        overlay.display.blit(border, rect.move(vec2(off)*TITLE_BD))
    if corner:
        for off in ((-1,-1),(-1,1),(1,-1),(1,1)):
            overlay.display.blit(border, rect.move(vec2(off)*TITLE_BD))
    overlay.display.blit(img, rect)

# Animate
def frame_time(time, anim_speed, length=None):
    frame_idx = (pg.time.get_ticks()-time) // anim_speed
    return frame_idx % length if length!=None else frame_idx

# Sides
def sides(status, anim, default='R'):
    if isinstance(anim, pg.Surface): anim = [anim]
    return {
        status+'_L': flips(anim, default!='L'),
        status+'_R': flips(anim, default!='R'),
    }

def sides4(status, T,B,R=(),L=()):
    return {
        status+'_T': T,
        status+'_B': B,
        status+'_L': L or flips(R),
        status+'_R': R or flips(L),
    }

# Vectors
def normalize(v):
    if v: return v.normalize()
    return v
def int_vector(v):
    return (int(v[0]),int(v[1]))