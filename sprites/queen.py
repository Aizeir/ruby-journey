from sprites.entity import Entity
from util.support import *

RANGE = TS*8
ATKZONE = (TS*2,TS)

class Queen(Entity):
    def __init__(self, data, world, groups):
        super().__init__(world, DUNGEON, data['pos'], groups, (48*SCALE,24*SCALE))

        self.spawn_pos = vec2(data.get('spawn', self.pos))
        self.speed *= 2

        self.dmg_img = world.damage_imgs[8]
        self.max_health = 10
        self.health = data.get('health',self.max_health)
        self.particles = []
        
        self.provoked = False
        self.timers['attack'] = Timer(300)
        self.timers['damage'] = Timer(1000)
        self.timers['dead'] = Timer(1000, self.die)
        self.attackzone = self.hitbox
    
    def save(self):
        return {"pos":tuple(self.pos),"health":self.health, "spawn":tuple(self.spawn_pos)}
        
    def load_graphics(self, world):
        ts = world.queen_imgs
        animation = {}
        self.shadows = {}

        def anim(n, imgs):
            anims, shadows = [],[]
            for img in imgs:
                shadow, img = get_shadow(img, 20*SCALE)
                shadows.append(shadow); anims.append(img)
            animation[n] = anims
            self.shadows[n] = shadows

        anim('idle_R', [ts[0]])
        anim('idle_L', flips([ts[0]],1))
        anim('move_R', [ts[0],ts[1]])
        anim('move_L', flips([ts[0],ts[1]],1))
        anim('attack_R', [ts[2]])
        anim('attack_L', flips([ts[2]],1))
        anim('damage_R', [ts[3]])
        anim('damage_L', flips([ts[3]],1))
        return animation
    
    
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
            if self.world.stones in sprite.groups() and sprite.hitbox.colliderect(self.hitbox):
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
                if sprite != self.world.player:
                    self.direction = (self.world.player.pos-self.pos).normalize()
                
    def get_status(self):
        if self.timers['attack'].active:
            self.status = "attack"
        elif self.direction.magnitude() != 0:
            self.status = "move"
        else:
            self.status = "idle"

        # BEHAVIOUR
        if self.status == "attack": return
        if self.status == "damage": return

        plr = self.world.player
        dist = self.pos.distance_to(plr.pos)
        self.attackzone = self.hitbox.inflate(*ATKZONE)
        
        # Transition (respawn/teleport)
        if plr.timers['dead'].active or self.world.timers['map'].active:
            self.direction = vec2()
            self.provoked = False
        # Attack (pas damage qd tp)
        elif self.hitbox.inflate(*ATKZONE).colliderect(plr.hitbox):
            self.direction = vec2()
            self.attack()
            self.provoked = True
        # Chase
        elif (dist > RANGE or not self.direction) and self.provoked:
            self.direction = (plr.pos-self.pos).normalize()

    def attack(self):
        self.timers['attack'].activate()
        plr = self.world.player
        plr.damage(1)
        plr.timers['knockback'].activate()
        plr.timers['knockback'].direction = (plr.pos-self.pos).normalize()*2
        
        # Status + Side
        x = plr.pos.x-self.pos.x
        if x:
            self.side = ('L','R')[x>0]

    def damage(self):
        if self.timers['dead'].active: return
        self.timers['damage'].activate()
        self.health -= 1
        self.provoked = True

        # FX
        sounds.hurtqueen.play()
        for _ in range(self.health*2):
            self.damage_pc()

        # Die
        if self.health == 0:
            self.timers['dead'].activate()

            self.status = "damage"
            self.timers['damage'].deactivate()

            sounds.deadqueen.play()
            for _ in range(self.max_health*4):
                self.damage_pc()
            
            for a in self.world.animals:
                if a.type == 'racoon':
                    a.diseappear()

            self.world.player.additem(12, 4)
            self.world.player.additem(10, 4)
            self.world.quests["queen"] = True
            
    def die(self):
        self.kill()
        sounds.yes.play()
        if self.world.pnjs['miner'].quest_idx == 1:
            self.world.overlay.open_dialog(*self.world.pnjs['miner'].complete_quest())
    
    def draw(self):
        # Dead
        if self.status == "damage":
            self.image.set_alpha((1-self.timers['dead'].percent())*255)
        
        # Zones
        elif self.provoked:
            # Damage zone
            ra = self.attackzone.move(-self.world.offset)
            r = self.rect.move(-self.world.offset)
            r.h = ra.y-r.y
            surf = pg.Surface(r.size)
            pg.draw.rect(surf, '#ff0000', (0,0,*r.size), 0, -1, 20, 20)
            surf.set_alpha(20)
            self.world.display.blit(surf, r)
            if self.timers['damage'].active: self.world.display.blit(surf, r)

            # Attack zone
            surf = pg.Surface(ra.size)
            pg.draw.rect(surf, '#ffffff', (0,0,*ra.size), 0, 20)
            surf.set_alpha(20)
            self.world.display.blit(surf, ra)
            if self.timers['attack'].active: self.world.display.blit(surf, ra)

        # Health
        if self.timers['damage'].active:
            surf = pg.Surface((64,24))
            surf.set_alpha((1-self.timers['damage'].percent())*255)
            surf.fill("#c38252")
            pg.draw.rect(surf, '#e0ba8b', (0,0,surf.get_width()*self.health/self.max_health,surf.get_height()))
            self.world.display.blit(surf, surf.get_rect(midbottom=self.rect.midtop-self.world.offset))

        # Draw
        return super().draw()

    def update(self, dt):
        if self.timers['dead'].active:
            self.timers['dead'].update()
            self.animate(dt)
            return
        super().update(dt)
