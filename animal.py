from util import *
from entity import Entity

RANGE = TS*2
HITBOXES = {'chicken':(12*SCALE,5*SCALE),'racoon':(12*SCALE,5*SCALE)}

class Animal(Entity):
    def __init__(self, data, world, groups):
        self.type = data[1]
        super().__init__(world, data[3], data[0], groups, HITBOXES[self.type], side=data[2])
        self.timers['move'] = Timer(1000, self.wander).activate()
        self.speed *= .8

        self.dmg_img = world.damage_imgs[4]
        self.max_health = 3
        self.health = data[-1] or self.max_health
        self.timers['damage'] = Timer(300)

        self.attacks = self.type != 'chicken'
        self.attack = False
        self.timers['diseappear'] = Timer(3000, self.kill)

    def save(self):
        return [(int(self.pos.x),int(self.pos.y)), self.type, self.side, self.map, self.health]
        
    def load_graphics(self, world):
        ts = world.animal_imgs[self.type]
        animation = {}
        self.shadows = {}

        def anim(n, imgs):
            anims, shadows = [],[]
            for img in imgs:
                shadow, img = get_shadow(img, 4*SCALE)
                shadows.append(shadow); anims.append(img)
            animation[n] = anims
            self.shadows[n] = shadows

        anim('idle_R', [ts[0]])
        anim('idle_L', flips([ts[0]],1))
        anim('move_R', [ts[0],ts[1]])
        anim('move_L', flips([ts[0],ts[1]],1))
        return animation

    def wander(self):
        self.timers['move'].activate()

        # Stop
        if self.direction:
            self.direction = vec2()
            self.timers['move'].duration = randint(3,5)*1000
        # Move random
        else:
            self.direction.x = choice((-1,1))
            self.direction.y = randint(-1,1)
            self.timers['move'].duration = 500

    def check_attack(self):
        if not self.attacks: return
        # Damage: keep direction
        if self.timers['damage'].active: return
        # Diseappear: keep direction
        if self.timers['diseappear'].active: return

        plr = self.world.player
        distance = self.pos.distance_to(plr.pos)

        # Stop attack ?
        stop_attack = False
        # Transition (respawning/teleporting)
        if plr.timers['dead'].active or self.world.timers['map'].active:
            stop_attack = True
        # Damage     (elif car pas damage lors de tp)
        elif self.hitbox.inflate(4*SCALE,4*SCALE).colliderect(plr.hitbox):
            stop_attack = True
            self.attack_player()
        # Player out of range
        if (self.attack and distance > RANGE):
            stop_attack = True

        # attack -> wander
        if stop_attack:
            self.attack = False # no attack
            self.wander()       # wander

        # wander -> attack
        elif not self.attack and distance <= RANGE:
            self.timers['move'].deactivate() # no wander
            self.attack = True               # attack
            self.direction = (plr.pos - self.pos).normalize()

    def attack_player(self):
        plr = self.world.player
        plr.damage()
        # Rotate animal
        x = plr.pos.x-self.pos.x
        if x:
            self.side = ('L','R')[x>0]
            
    def damage(self, x):
        self.health -= x
        self.timers['damage'].activate()
        
        # FX
        sounds.hurt.play()
        for _ in range(int(self.health)):
            self.damage_pc()

        # Die
        if self.health <= 0:
            self.health = 0
            self.die()
        # Flee
        else:
            self.attack = False            # no attack
            self.timers['move'].activate() # flee (3s) -> wander
            self.timers['move'].duration = 3000
            self.direction.x = choice((-1,1))
            self.direction.y = randint(-1,1)

    def die(self):
        for _ in range(self.max_health):
            self.damage_pc()

        self.kill()
        sounds.dead.play()

        if self.type == 'chicken':
            self.world.player.additem(10)
        elif self.type == 'racoon':
            self.world.player.additem(12)

    def diseappear(self):
        self.direction.x = choice((-1,1))
        self.direction.y = randint(-1,1)
        self.timers['diseappear'].activate()
        self.timers['move'].deactivate()

    def draw(self):
        # Health bar
        if self.timers['damage'].active:
            surf = pg.Surface((24,12))
            surf.set_alpha((1-self.timers['damage'].percent())*255)
            surf.fill("#734d5c")
            pg.draw.rect(surf, '#a76772', (0,0,int(surf.get_width()*self.health/self.max_health),surf.get_height()))
            self.world.display.blit(surf, surf.get_rect(midbottom=self.rect.midtop+vec2(0,-4)-self.world.offset))

        # Diseappear
        if self.timers['diseappear'].active:
            self.image.set_alpha((1-self.timers['diseappear'].percent())*255)
            self.shadow.set_alpha((1-self.timers['diseappear'].percent())*255)

        return super().draw()

    def update(self, dt):
        self.check_attack()
        super().update(dt)

