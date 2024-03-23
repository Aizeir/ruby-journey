from util.support import *
from sprites.sprite import Sprite


class Entity(Sprite):
    """ 
    The Entity object.
    includes Status, Movement, Collisions (+ Timers)
    """
    def __init__(self, world, map, pos, groups, hitbox=None, status='idle',side='R'):
        super().__init__(world, map, pos, self.load_graphics(world), groups, hitbox, status, side)
        
        # Movement
        self.direction = vec2()
        self.speed = 50*SCALE

        # Collision
        self.hitbox_offset = self.pos-self.rect.center
        self.set_position(pos)

        # Timers
        self.timers = {
            #"timer": Timer(200),
        }

    def load_graphics(self, world):
        return {}

    def get_side(self):
        if self.direction.x:
            self.side = ("L","R")[self.direction.x>0]
    
    def get_status(self):
        """ Compute entity status. """
        # Idle
        if self.direction.magnitude() == 0:
            self.status = "idle"
        else:
            self.status = "move"

    def set_position(self, pos=None):
        """ Set position (regardless collisions). """
        self.hitbox.center = pos or self.hitbox.center
        self.rect.center = self.hitbox.center - self.hitbox_offset
        self.pos = vec2(self.hitbox.center)

    def move(self, dt):
        # Normalize direction
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        
        # Apply movement
        self.hitbox.centerx += round(self.direction.x * self.speed * dt)
        self.collision("h")
        self.hitbox.centery += round(self.direction.y * self.speed * dt)
        self.collision("v")

        self.set_position()

    def collision(self, direction):
        for sprite in self.world.collides_filter:
            if sprite != self and sprite.hitbox.colliderect(self.hitbox):
                if direction == "h":
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    elif self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
                elif direction == "v":
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    elif self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom
        
    def animate(self, dt):
        res = super().animate(dt)
        self.rect = self.image.get_rect(center=self.pos-self.hitbox_offset)
        return res

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def update(self, dt):
        super().update(dt)
        self.get_side()
        self.get_status()
        self.move(dt)
        self.update_timers()
