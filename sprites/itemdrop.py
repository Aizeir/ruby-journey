from math import sin
from sprites.sprite import Sprite
from util.support import *

class ItemDrop(Sprite):
    def __init__(self, data, world, groups):
        self.item, self.amount = int(data[3]), int(data[4])

        img = world.items_imgs[self.item]
        surf = pg.Surface((TS+2*SCALE,TS+2*SCALE), pg.SRCALPHA, 32)
        border = pg.mask.from_surface(img).to_surface(unsetcolor=(0,0,0,0),setcolor="#f7efc7")
        surf.blit(border, (0,SCALE))
        surf.blit(border, (2*SCALE,SCALE))
        surf.blit(border, (SCALE,0))
        surf.blit(border, (SCALE,2*SCALE))
        surf.blit(img, (SCALE,SCALE))
        super().__init__(world, data[2], (int(data[0]),int(data[1])), surf, groups)
        
    def save(self):
        return f"{self.rect.x} {self.rect.y} {self.map} {self.item} {self.amount}"
    
    def update(self, dt):
        self.image.set_alpha(255*abs(sin(pg.time.get_ticks()*math.pi*2/5000)))
        plr = self.world.player
        if plr.can_additem(self.item, self.amount) and self.rect.colliderect(plr.hitbox):
            self.kill()
            sounds.collect.play()
            self.world.player.additem(self.item, self.amount)