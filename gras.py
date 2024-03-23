import pygame as pg
from util.support import *

pg.init()
display = pg.display.set_mode((W,H))
# Floor and logo
offset = 0
speed = 2
floor = pg.Surface((W*2, H))
floor.fill(WILDCOLOR)

SIZE = TS
details = load_tileset('tilesets/details', size=(SIZE,SIZE))[:8]
for     y in range(0,floor.get_height(),SIZE):
    for x in range(0,floor.get_width(),SIZE):
        if not proba(2): continue
        floor.blit(details[randint(0,len(details)-1)],(x,y))

for i in range(floor.get_width()//speed):
    for e in pg.event.get():
        if e.type == pg.QUIT:
            pg.quit()
            exit()

    display.fill('black')
    offset += speed
    if offset > floor.get_width()-W:
        display.blit(floor, (-offset+floor.get_width(),0))
    display.blit(floor, (-offset,0))
    
    pg.image.save(display, "_recs/rq/"+str(i)+".png")
    pg.display.flip()