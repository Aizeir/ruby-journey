from util import *
from components import *

class Sprite(pg.sprite.Sprite):
    def __init__(self, world, map, pos, anim, hitbox=None, status=None):
        super().__init__(world.sprites)
        self.world = world
        self.map = map

        self.animation = Animation(self, anim, status, self.anim_end)
        self.shadow = getattr(self, "shadow", None)

        self.rect = self.image.get_frect(topleft=pos)
        self.collision = Collision(self, world, pos, hitbox)
        
    @property
    def hitbox(self): return self.collision.hitbox
    @hitbox.setter
    def hitbox(self, val): self.collision.hitbox = val
    @property
    def pos(self): return vec2(self.hitbox.center)
 
    def anim_end(self):
        pass
    
    def damage_pc(self, img=None):
        self.world.damage_pc.new(
            vec2(randint(self.rect.x,self.rect.right),randint(self.rect.y,self.rect.bottom)),
            image=(img or self.dmg_img).copy(),
            floor=self.rect.bottom,
            #group=self.particles
        )
    
    def draw(self):
        # draw rect
        self.draw_rect = self.rect.move(-self.world.offset)
        # shadow
        if self.shadow:
            self.world.display.blit(self.shadow, self.shadow.get_rect(midtop=self.draw_rect.midbottom))
        # image
        self.world.display.blit(self.image, self.draw_rect)

    def update(self, dt):
        # animation
        self.animation.update(dt)
        # shadow anim
        if hasattr(self, 'shadows'):
            self.shadow = self.shadows[self.animation.status][int(self.animation.frame_idx)]
        














class Entity(Sprite):
    def __init__(self, world, map, pos, groups, hitbox=None, status='idle_R'):
        super().__init__(world, map, pos, self.load_graphics(world), groups, hitbox, status)
        
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
