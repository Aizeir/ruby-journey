from util import *


class Collision:
    def __init__(self, sprite, world, hitbox):
        if not hitbox:
            self.hitbox = None; return
        elif hitbox == True:
            self.hitbox = sprite.rect; return
        elif isinstance(hitbox, pg.Rect):
            self.hitbox = hitbox.move(sprite.rect.topleft)
        else:
            shadow_height = hitbox[2] if len(hitbox)==3 else 0
            self.hitbox = pg.Rect((0,0),hitbox[:2]).move_to(midbottom=sprite.rect.midbottom-vec2(0,shadow_height))
        
        self.offset = self.hitbox.topleft - vec2(sprite.rect.topleft)
        sprite.add(world.collides)


class Animation:
    def __init__(self, sprite, anim, status=None, end=lambda:True, new_frame=lambda:None):
        self.sprite = sprite
        self.animation = anim
        self.status = status
        self.frame_idx = 0
        self.anim_speed = ANIM_SPEED

        self.new_frame = new_frame
        self.end = end

        self.sprite.image = self.get_image()
        
    @property
    def is_image(self): return isinstance(self.animation, pg.Surface)
    @property
    def frames(self):
        return self.animation[self.status] if isinstance(self.animation, dict) else self.animation
    def get_image(self):
        return self.frames if self.is_image else self.frames[int(self.frame_idx)]

    def set_status(self, status):
        self.status = status
        self.frame_idx = 0
    
    def update(self, dt):
        if self.is_image: return

        # Incrase frame idx
        old = self.frame_idx
        self.frame_idx += self.anim_speed * dt
        # New frame
        if int(self.frame_idx) > old:
            self.new_frame()
        # End of anim
        if self.frame_idx >= len(self.frames):
            if self.end():
                self.frame_idx = 0

        # Update image
        self.sprite.image = self.get_image()
            

class Movement:
    def __init__(self, sprite):
        self.sprite = sprite
        self.direction = vec2()
        self.side = 'R'
        self.collisions = {'L':[],'R':[],'T':[],'B':[],'all':[]}

    @property
    def moving(self): return bool(self.direction)

    def update(self, dt, side=True):
        if not self.direction: return
        
        # Get side
        if self.direction.x and side:
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
    def __init__(self, max, value=None, die=None, cooldown=0):
        self.max = max
        self.value = value if value!=None else max
        self.cooldown = Timer(cooldown)

        self.die = die or (lambda:None)

    @property
    def percent(self): return self.value / self.max
    @property
    def dead(self): return self.value == 0

    def __add__(self, x): self.add(+x); return self
    def __sub__(self, x): self.add(-x); return self
    def __eq__(self, x): return x == self.value
    def __repr__(self): return f"{self.value}"
    def __bool__(self): return self.value > 0

    def on_die(self, func):
        self.die = func

    def add(self, x):
        if self.dead or self.cooldown.active: return

        self.value = clamp(0, self.value+x, self.max)
        if self.dead:
            self.die()
        else:
             self.cooldown.activate()

    def update(self, dt):
        self.cooldown.update()

