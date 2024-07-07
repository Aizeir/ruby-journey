from util import *
from components import *

class Sprite(pg.sprite.Sprite):
    def __init__(self, world, map, pos, anim, hitbox=None, status=None, center=False, health=None, max_health=1):
        super().__init__(world.sprites)
        self.world = world
        self.map = map

        self.animation = Animation(self, anim, status, self.anim_end, self.anim_new)
        
        self.rect = self.image.get_rect(topleft=pos)
        self.collision = Collision(self, world, hitbox)
        if center: self.pos = pos

        self.health = Health(max_health, health, self.die, 300)
        self.damage_imgs = []
        self.drops = []

    @property
    def hitbox(self): return self.collision.hitbox
    @hitbox.setter
    def hitbox(self, val): self.collision.hitbox = val
    @property
    def pos(self): return vec2(self.hitbox.center)
    @pos.setter
    def pos(self, pos):
        self.hitbox.center = pos
        self.rect.center = self.hitbox.center - self.collision.offset
    @property
    def pos_int(self): return int_vector(self.pos)
    @property
    def pos_save(self): return int_vector(self.rect.center)
    
    def anim_new(self): pass
    def anim_end(self): return True
    
    def damage(self, x=1):
        if self.health.cooldown.active: return
        if self.health.dead: return
        # health reduce
        self.health -= x
        # particles
        for _ in range(self.health.value):
            self.damage_pc()
        return True
        
    def damage_pc(self, particle=None):
        self.world.damage_pc.new(
            vec2(randint(self.rect.x,self.rect.right),randint(self.rect.y,self.rect.bottom)),
            particle=particle or choice(self.damage_imgs),
            floor=self.rect.bottom,
        )

    def die(self, kill=True):
        # damage particles
        for _ in range(self.health.max):
            self.damage_pc()
        # drops
        if self.drops:
            for drop in self.drops:
                self.world.player.additem(*drop)
        # kill
        if kill:
            self.kill()

    def draw_health_bar(self):
        if self.health.cooldown.active:
            surf = pg.Surface((24,12))
            surf.set_alpha((1-self.health.cooldown.percent())*255)
            surf.fill("#734d5c")
            pg.draw.rect(surf, '#a76772', (0,0,surf.get_width()*self.health.percent,surf.get_height()))
            self.world.display.blit(surf, surf.get_rect(midbottom=self.draw_rect.midtop+vec2(0,-4)))

    def draw(self):
        # draw rect
        self.draw_rect = self.rect.move(-self.world.offset)
        # health bar
        self.draw_health_bar()
        # image
        self.world.display.blit(self.image, self.draw_rect)

    def update(self, dt):
        self.animation.update(dt)
        self.health.update(dt)

class Entity(Sprite):
    def __init__(self, world, map, pos, anim, hitbox=None, status='idle_R', health=None, max_health=1):
        super().__init__(world, map, pos, anim, hitbox, status, center=True, health=health, max_health=max_health)
        # Movement
        self.movement = Movement(self)
        self.speed = 50*SCALE

        # Timers
        self.timers = {}

    @property
    def status(self):
        return self.animation.status.split("_")[0]
    @status.setter
    def status(self, status):
        # Reset animation (new anim)
        if status not in self.animation.status:
            self.animation.frame_idx = 0
        # Set status
        self.animation.status = f"{status}_{self.movement.side}"

    def format_direction(self, direction):
        if direction:
            self.movement.direction = direction
        if self.movement.direction:
            self.movement.direction = normalize(self.movement.direction) * self.speed

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def update(self, dt):
        self.update_timers()
        self.movement.update(dt)
        self.animation.update(dt)
        self.health.update(dt)
