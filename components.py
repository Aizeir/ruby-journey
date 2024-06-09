from util import *


class Collision:
    def __init__(self, sprite, world, pos, hitbox):
        if not hitbox:
            self.hitbox = None
            return
        
        sprite.add(world.collides)
        self.hitbox = hitbox.move(pos)
        self.offset = self.hitbox.topleft - vec2(pos)
        

class Animation:
    def __init__(self, sprite, anim, status=None, end=lambda:None):
        self.sprite = sprite
        self.animation = anim
        self.status = status
        self.frame_idx = 0
        self.anim_speed = ANIM_SPEED
        self.end = end

        self.sprite.image = self.image

    def on_end(self, func): self.end = func

    @property
    def is_image(self): return isinstance(self.animation, pg.Surface)
    @property
    def frames(self):
        return self.animation[self.status] if isinstance(self.animation, dict) else self.animation
    @property
    def image(self):
        return self.frames if self.is_image else self.frames[int(self.frame_idx)]

    def set_status(self, status):
        self.status = status
        self.frame_idx = 0
    
    def update(self, dt):
        if self.is_image: return
        # Animate
        self.frame_idx += self.anim_speed * dt
        if self.frame_idx >= len(self.frames) and not self.end():
            self.frame_idx = 0
        self.sprite.image = self.image
            
class Movement:
    def __init__(self, sprite):
        self.sprite = sprite
        self.direction = vec2()
        self.side = 'R'
        self.collisions = {'L':[],'R':[],'T':[],'B':[],'all':[]}

    @property
    def moving(self): return bool(self.direction)

    def update(self, dt):
        if not self.direction: return
        
        # Get side
        if self.direction.x:
            self.side = 'LR'[self.direction.x>0]

        # Movement vector
        sprite = self.sprite
        movement = self.direction * dt
        self.collisions = {'L':[],'R':[],'T':[],'B':[],'all':[]}

        # Simple move
        if not sprite.hitbox:
            sprite.rect.move_ip(movement)
            return
        
        # Collision X
        sprite.hitbox.x += movement.x
        for obj in sprite.world.collides_filter:
            if obj == sprite: continue
            if sprite.hitbox.colliderect(obj.hitbox):
                if   movement.x>0:
                    self.collisions['R'].append(obj)
                    self.collisions['all'].append(obj)
                    sprite.hitbox.right = obj.hitbox.left
                elif movement.x<0:
                    self.collisions['L'].append(obj)
                    self.collisions['all'].append(obj)
                    sprite.hitbox.left = obj.hitbox.right

        # Collision Y
        sprite.hitbox.y += movement.y
        sprite.hitbox.centery = max(0,sprite.hitbox.centery)
        for obj in sprite.world.collides_filter:
            if obj == sprite: continue
            if sprite.hitbox.colliderect(obj.hitbox):
                if   movement.y>0:
                    self.collisions['B'].append(obj)
                    self.collisions['all'].append(obj)
                    sprite.hitbox.bottom = obj.hitbox.top
                elif movement.y<0:
                    self.collisions['T'].append(obj)
                    self.collisions['all'].append(obj)
                    sprite.hitbox.top = obj.hitbox.bottom

        # Update rect
        sprite.rect.topleft = sprite.hitbox.topleft - sprite.collision.offset
        
class Health:
    def __init__(self, max, value=None, die=None):
        self.max = max
        self.value = value if value!=None else max

        self.die = die or (lambda:None)

    def on_die(self, func): self.die = func

    @property
    def percent(self): return self.value / self.max

    def add(self, x):
        if self.value == 0: return
        self.value = clamp(0, self.value+x, self.max)
        if self.value == 0: self.die()

    def __add__(self, x): self.add(+x); return self
    def __sub__(self, x): self.add(-x); return self
    def __eq__(self, x): return x == self.value
    def __repr__(self): return f"{self.value}"
    def __bool__(self): return self.value > 0
