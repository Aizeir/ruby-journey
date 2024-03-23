import pygame as pg
pg.init()
import os, time, sys, json, moderngl
from threading import Thread
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

# Font
def font(path, size):
    try: return pg.font.Font(res("assets/ui/"+path), size)
    except: return pg.font.SysFont(path, size)
# Text
def textr(text, font, color, **k):
    t = font.render(text, False, color)
    return t, t.get_rect(**k)
def rectx(size, name, val):
    r = pg.Rect((0,0), size)
    setattr(r, name, val)
    return r
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
def load(image, scale=0, flip_x=False, flip_y=False, rotate=0, size=None, colorkey=None):
    if isinstance(image, str):
        image = pg.image.load(res("assets/"+image+".png")).convert_alpha()
    if scale:
        size = vec2(image.get_size())*scale
    if size:
        image = pg.transform.scale(image, size)
    if flip_x or flip_y:
        image = pg.transform.flip(image, flip_x, flip_y)
    if rotate:
        image = pg.transform.rotate(image, rotate)
    if colorkey:
        image.set_colorkey(colorkey)
    return image

def flips(images, x=0, y=0):
    return tuple(pg.transform.flip(i,x,y) for i in images)

def load_folder(path, func, *a,**k):
    """ List of all images in folder """
    images = []

    for _, _, files in os.walk("assets/"+path):
        for filename in files:
            images.append(func(f"{path}/{filename}", *a,**k))
    
    return images

def load_folder_dict(path, func, *a,**k):
    """ All {name: image} in folder """
    image_dict = {}

    for _, _, files in os.walk("assets/"+path):
        for filename in files:
            name = filename.split(".")[0]
            image_dict[name] = func(f"{path}/{name}", *a,**k)

    return image_dict

def load_tileset(path, size=TILEINT, scale=SCALE):
    image = load(path, scale=scale)
    
    tilemap = []
    for y in range(image.get_height()//size[1]):
        for x in range(image.get_width()//size[0]):
            tilemap.append(image.subsurface((x*size[0], y*size[1], size[0], size[1])))
    return tilemap

# Math
def rect_add(rect, rect2):
    return pg.Rect(rect[0]+rect2[0],rect[1]+rect2[1],rect[2]+rect2[2],rect[3]+rect2[3])

# Shaders
def load_shader(name):
    with open(res(f"assets/shaders/{name}"), 'r') as file:
        return file.read()

def texture(ctx, surf):
    tex = ctx.texture(surf.get_size(), 4)
    tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
    tex.swizzle = 'BGRA'
    tex.write(surf.get_view('1'))
    return tex

def render(tex, render, **uniforms):
    if isinstance(tex, pg.Surface):
        tex = texture(render.ctx, tex)

    textures = [tex]
    tex.use(0)

    for uniform, value in uniforms.items():
        if isinstance(value, pg.Surface):
            value = texture(render.ctx, value)
        if isinstance(value, moderngl.Texture):
            value.use(len(textures))
            render.program[uniform] = len(textures)
            textures.append(value)
        else:
            render.program[uniform] = value
    render.render(mode=moderngl.TRIANGLE_STRIP)

    for i, t in enumerate(textures):
        t.release()

# shadow
def get_shadow(img, size):
    return\
        img.subsurface(0, img.get_height()-size, img.get_width(), size),\
        img.subsurface(0, 0, img.get_width(), img.get_height()-size)

# outline (ui)
def ui_outline(overlay, img, color=UI[1], corner=False, big=True, **k):
    if isinstance(img, str):
        img, rect = textr(img, (overlay.font, overlay.fontbig)[big], UI[6], **k)
    else:
        img, rect = img, img.get_rect(**k)
        
    border = pg.mask.from_surface(img).to_surface(unsetcolor=(0,0,0,0),setcolor=color)
    overlay.display.blit(border, rect.move(-TITLE_BD,0))
    overlay.display.blit(border, rect.move(+TITLE_BD,0))
    overlay.display.blit(border, rect.move(0,-TITLE_BD))
    overlay.display.blit(border, rect.move(0,+TITLE_BD))
    if corner:
        overlay.display.blit(border, rect.move(-TITLE_BD,-TITLE_BD))
        overlay.display.blit(border, rect.move(+TITLE_BD,-TITLE_BD))
        overlay.display.blit(border, rect.move(-TITLE_BD,+TITLE_BD))
        overlay.display.blit(border, rect.move(+TITLE_BD,+TITLE_BD))
    overlay.display.blit(img, rect)