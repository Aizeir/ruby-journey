from sprite import Entity
from util import *

RANGE = TS*8
ATKZONE = (TS*2,TS)

class Queen(Entity):
    def __init__(self, data, world):
        super().__init__(world, map=DUNGEON, pos=data['pos'], anim=world.imgs['queen'], hitbox=QUEEN_HITBOX)
        self.add(world.animals_queen)

        self.spawn_pos = data.get('spawn', self.pos_int)
        self.speed *= 2

        self.health.max = 10
        self.health.value = data.get('health',self.health.max)
        self.health.cooldown = 1000
        self.damage_imgs = [8]
        self.drops = [[12,4],[10,4]]

        self.provoked = False
        self.timers['attack'] = Timer(300)
        self.timers['dead'] = Timer(1000, self.final_die)
        self.attack_zone = self.hitbox
    
    def save(self):
        return {"pos":self.pos_save, "health":self.health.value, "spawn":self.spawn_pos}
        
    @property
    def dead(self): return self.health.dead

    def attack(self):
        self.timers['attack'].activate()
        plr = self.world.player
        vec = plr.pos-self.pos

        # Damage player
        plr.damage(1)
        plr.timers['knockback'].activate()
        plr.timers['knockback'].dir = normalize(vec)*2
        
        # Side
        if vec.x:
            self.movement.side = ('L','R')[vec.x>0]

    def damage(self):
        if self.dead: return
        
        if super().damage():
            self.provoked = True
            
            # More FX
            sounds.hurtqueen.play()
            for _ in range(self.health.value):
                self.damage_pc()

    def die(self):
        self.timers['dead'].activate()
        self.status = "damage"
        super().die(False)
        
        # Queen quest
        self.world.quests["queen"] = True

        # More FX
        sounds.deadqueen.play()
        for _ in range(self.health.max*3):
            self.damage_pc()
        
        # Diseappear
        for a in self.world.animals:
            if a.name == 'racoon':
                a.diseappear()
            
    def final_die(self):
        self.kill()
        sounds.yes.play()
        # Dialog miner
        if self.world.pnjs['miner'].quest_idx == 1:
            self.world.overlay.open_dialog(*self.world.pnjs['miner'].complete_quest())
    
    def draw(self):
        # Dead
        if self.dead:
            self.image.set_alpha((1-self.timers['dead'].percent())*255)
        
        # Zones
        elif self.provoked:
            # Damage zone
            ra = self.attack_zone.move(-self.world.offset)
            r = self.rect.move(-self.world.offset)
            r.h = ra.y-r.y
            surf = pg.Surface(r.size)
            pg.draw.rect(surf, '#ff0000', (0,0,*r.size), 0, -1, 20, 20)
            surf.set_alpha(20)
            
            self.world.display.blit(surf, r)
            if self.health.cooldown.active:
                self.world.display.blit(surf, r)

            # Attack zone
            surf = pg.Surface(ra.size)
            pg.draw.rect(surf, '#ffffff', (0,0,*ra.size), 0, 20)
            surf.set_alpha(20)
            self.world.display.blit(surf, ra)
            if self.timers['attack'].active:
                self.world.display.blit(surf, ra)

        # Draw
        return super().draw()

    def update(self, dt):
        # Dead
        if self.dead:
            self.timers['dead'].update()
            self.animation.update(dt)
            return
    
        # Behaviour
        if self.status not in ("damage", "attack"):
            plr = self.world.player
            dist = self.pos.distance_to(plr.pos)
            self.attack_zone = self.hitbox.inflate(*ATKZONE)
            
            # - Transition (respawn/teleport)
            if plr.dead or self.world.timers['map'].active:
                self.movement.direction = vec2()
                self.provoked = False
            # - Attack (pas damage qd tp)
            elif self.hitbox.inflate(*ATKZONE).colliderect(plr.hitbox):
                self.movement.direction = vec2()
                self.attack()
                self.provoked = True
            # - Chase
            elif (dist > RANGE or not self.movement.direction) and self.provoked:
                self.format_direction(plr.pos-self.pos)

        # Status
        if self.timers['attack'].active:
            self.status = "attack"
        else:
            self.status = ("idle","move")[self.movement.moving]

        # Update
        super().update(dt)
