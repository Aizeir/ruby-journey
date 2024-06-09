from animal import Animal
from prop import Prop
from queen import Queen
from util.prop_data import PROP_DATA
from util import *
from sprite import Sprite


class Pebble(Sprite):
    def __init__(self, plr, pos, dir, groups):
        super().__init__(plr.world, plr.map, pos, plr.world.pebble_img, groups)

        self.direction = dir
        self.range = 6*TS
        self.speed = 800
        self.dmg_img = self.world.damage_imgs[7]
        
        self.height = plr.rect.bottom - pos[1]
        self.set_position(pos)
        self.spawn = pos

    def set_position(self, pos):
        self.rect.center = pos
        self.pos = vec2(pos)
        self.hitbox.center = pos+vec2(0,self.height)

    def update(self, dt):
        self.set_position(self.pos + self.direction * self.speed * dt)
        
        # Out of range
        if self.pos.distance_to(self.spawn) > self.range:
            sounds.stone.play()
            self.kill()
            self.world.damage_pc.new(
                self.pos,
                image=self.dmg_img.copy(),
                floor=self.pos.y+self.height,
            )
            pass
        
        # Collision prop
        for s in self.world.collides_filter:
            # Player ?!
            if s == self.world.player: continue
            # Small props
            if isinstance(s,Prop) and 'small' in PROP_DATA[s.name]: continue
            # Lakes
            if self.world.waters in s.groups(): continue

            # Collide
            if s.hitbox.colliderect(self.rect):
                sounds.stone.play()
                self.kill()
                self.world.damage_pc.new(
                    self.pos,
                    image=self.dmg_img.copy(),
                    floor=self.pos.y+self.height,
                )
                    
                # Damage ?
                if isinstance(s,Animal):
                    s.damage()
                elif isinstance(s,Queen):
                    s.provoked = True