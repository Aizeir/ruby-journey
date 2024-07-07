from util import *
from sprite import Entity

RANGE = TS*2

class Animal(Entity):
    def __init__(self, data, world):
        self.name = data[1]
        
        super().__init__(world, map=data[3], pos=data[0], anim=world.imgs['animal'][self.name], hitbox=ANIMAL_HITBOX[self.name], status='idle_'+data[2])
        self.add(world.animals, world.animals_queen)

        # Movement
        self.speed *= .8
        self.timers['move'] = Timer(1000, self.wander).activate()

        # Health
        self.health.max = 3
        self.health.value = data[-1] or self.health.max
        self.health.cooldown.duration = 300

        self.damage_imgs = [4]
        self.drops = {'chicken': [10], 'racoon': [12]}[self.name]

        # Attacking
        self.attacking = False
        self.do_attack = self.name != 'chicken'

        # Cutscene: diseappear
        self.timers['diseappear'] = Timer(3000, self.kill)

    def save(self):
        return [self.pos_save, self.name, self.movement.side, self.map, self.health.value]

    def random_dir(self):
        self.format_direction(vec2(choice((-1,1)), randint(-1,1)))

    def wander(self):
        self.timers['move'].activate()

        # Stop
        if self.movement.direction:
            self.timers['move'].duration = randint(3,5)*1000
            self.movement.direction = vec2()
        # Move random
        else:
            self.timers['move'].duration = 500
            self.random_dir()

    def check_attack(self):
        if not self.do_attack: return
        # Damage: keep direction
        if self.health.cooldown.active: return
        # Diseappear: keep direction
        if self.timers['diseappear'].active: return

        plr = self.world.player
        distance = self.pos.distance_to(plr.pos)

        # Stop attack ?
        stop_attack = False
        # Transition (respawning/teleporting)
        if plr.dead or self.world.timers['map'].active:
            stop_attack = True
        # Damage (elif car pas damage lors de tp)
        elif self.hitbox.inflate(4*SCALE,4*SCALE).colliderect(plr.hitbox):
            stop_attack = True
            self.attack_player()
        # Player out of range
        if self.attacking and distance > RANGE:
            stop_attack = True

        # attack -> wander
        if stop_attack:
            self.attacking = False # no attack
            self.wander()         # wander

        # wander -> attack
        elif not self.attacking and distance <= RANGE:
            self.timers['move'].deactivate() # no wander
            self.attacking = True               # attack
            self.format_direction(plr.pos - self.pos)

    def attack_player(self):
        self.world.player.damage()
        # Rotate animal
        self.side = ('L','R')[self.world.player.pos.x>self.pos.x]
            
    def damage(self, x=1):
        if super().damage(x):
            sounds.hurt.play()
        
            # Flee
            if self.health:
                self.attacking = False         # no attack
                self.timers['move'].activate() # flee (3s) -> wander
                self.timers['move'].duration = 3000
                self.random_dir()

    def die(self):
        sounds.dead.play()
        super().die()

    def diseappear(self):
        self.random_dir()
        self.timers['diseappear'].activate()
        self.timers['move'].deactivate()

    def draw(self):
        # Diseappear
        if self.timers['diseappear'].active:
            self.image.set_alpha((1-self.timers['diseappear'].percent())*255)
        super().draw()

    def update(self, dt):
        self.check_attack()
        self.status = ('idle','move')[self.movement.moving]
        super().update(dt)
