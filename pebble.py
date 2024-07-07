from sprites.animal import Animal
from prop import Prop
from queen import Queen
from util.prop_data import PROP_DATA
from util import *
from sprite import Sprite


PEBBLE_RANGE = 6*TS

class Pebble(Sprite):
    def __init__(self, plr, pos, direction):
        super().__init__(plr.world, map=plr.map, pos=pos, anim=plr.world.imgs['pebble'], hitbox=True)

        # Movement
        self.direction = normalize(direction)
        self.speed = 600
        
        self.height = plr.rect.bottom - pos[1]
        self.pos = pos
        self.spawn = pos

    @property
    def pos(self): return vec2(self.rect.center)
    @pos.setter
    def pos(self, pos): self.rect.center = pos

    def damage_pc(self):
        self.world.damage_pc.new(
            self.pos,
            particle=7,
            floor=self.pos.y+self.height,
        )

    def die(self):
        sounds.stone.play()
        self.damage_pc()
        self.kill()

    def update(self, dt):
        self.pos += self.direction * self.speed * dt
        
        # Out of range
        if self.pos.distance_to(self.spawn) > PEBBLE_RANGE:
            self.die()
            return
        
        # Collision prop
        for s in self.world.collides_filter:
            # Player ?
            if s == self.world.player: continue
            # Small props
            if isinstance(s,Prop) and 'small' in PROP_DATA[s.name]: continue
            # Lakes
            if self.world.waters in s.groups(): continue

            # Collide
            if s.hitbox.colliderect(self.rect):
                # Kill pebble
                self.die()
                    
                # Damage abimal
                if isinstance(s,Animal):
                    s.damage()
                elif isinstance(s,Queen):
                    s.provoked = True