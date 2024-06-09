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
        

class Sprite(pg.sprite.Sprite):
    """ 
    The generic Sprite.
    includes Animation, Hitbox, Health
    """
    def __init__(self, world, map, pos, anim, groups, hitbox=None, status=None, side=None):
        super().__init__(groups)
        self.map = map
        self.world = world

        # Animation
        self.image = anim
        
        self.animated = isinstance(anim, dict)
        if self.animated:
            self.animation = anim
            self.frame_idx = 0
            
            self.status, self.side = status, side
            status = self.status+"_"+self.side if self.status and self.side else self.status or self.side
            self.image = anim[status][0]
        
        # Rect
        self.rect = self.image.get_rect(topleft = pos)

        if isinstance(hitbox, pg.Rect):
            self.hitbox = hitbox.move(pos)
        else:
            self.hitbox = pg.Rect((0,0),hitbox or self.image.get_size())
            self.hitbox.midbottom = self.rect.midbottom

        self.pos = vec2(self.hitbox.center)

        # shadow
        self.shadow = getattr(self, "shadow", None)

        # Particles
        #self.particles = []

    def animate(self, dt):
        if not self.animated: return
        
        status = self.status+"_"+self.side if self.status and self.side else self.status or self.side
        if status not in self.animation: return
        
        old_fidx = self.frame_idx
        self.frame_idx += ANIM_SPEED * dt
        self.frame_idx %= len(self.animation[status])
        self.update_image(status)

        if getattr(self, 'shadows', None):
            self.shadow = self.shadows[status][int(self.frame_idx)]
        
        return self.frame_idx < old_fidx
    
    def update_image(self, status=None):
        status = status or self.status+"_"+self.side if self.status and self.side else self.status or self.side
        self.image = self.animation[status][int(self.frame_idx)]

    def damage_pc(self, img=None):
        self.world.damage_pc.new(
            vec2(randint(self.rect.x,self.rect.right),randint(self.rect.y,self.rect.bottom)),
            image=(img or self.dmg_img).copy(),
            floor=self.rect.bottom,
            #group=self.particles
        )
    
    def draw(self):
        if self.shadow:
            self.world.display.blit(self.shadow, self.shadow.get_rect(midtop=self.rect.midbottom-self.world.offset))
        self.world.display.blit(self.image, self.rect.move(-self.world.offset))
        
    def update(self, dt):
        self.animate(dt)
