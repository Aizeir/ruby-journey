from sprite import Sprite
from util.prop_data import PROP_DATA
from util import *
from components import *

class Prop(Sprite):
    def __init__(self, data, world, center=False):
        # Name
        self.name = data[2]
        anim_name = self.name if self.name!='tree' else choice(('tree','tree2'))

        # Info (for all trees) and data (for specific tree)
        info = PROP_DATA[self.name]
        self.data = data[5] if len(data)>5 else None

        # Init
        super().__init__(world, map=data[3], pos=int_vector(data[0:2]), anim=world.imgs['props'][anim_name], hitbox=info['hitbox'], center=center)
        self.add(world.props)

        # Health
        self.health.max = info.get('health',1)
        self.health.value = int(data[4]) if data[4] else self.health.max
        self.health.cooldown.duration = 300

        self.damage_imgs = info.get('damage', [0])
        self.drops = [info.get('drop')]
        self.tool = info.get('tool')

        # Alpha
        self.alpha_timer = Transition(200, 100)
        self.plr_behind = False

        # Teleport / Other name-depending
        if 'teleport' in info:
            self.add(world.interacts)
            
            if self.name == 'hole':
                self.world.teleport_pos[self.name] = (self.map, self.rect.midtop+vec2(0,-TS/2))
            elif 'stair' in self.name:
                self.world.teleport_pos[self.name] = (self.map, self.rect.midright+vec2(TS/2,0))
            else:
                self.world.teleport_pos[self.name] = (self.map, self.rect.midbottom+vec2(0,TS/2))
        elif self.name == 'abandoned':
            self.world.barn = self
            if self.data == "d":
                self.image = self.world.props_imgs['barn_destroy']
        elif self.name == 'boat' and not self.world.ended:
            self.add(world.interacts)
        elif self.name == 'fruit_tree':
            if self.data:
                self.data = json.loads(self.data) 
                if self.data[0] == 'fruit':
                    self.add(self.world.interacts)
            else:
                self.data = ['water']

        # Minimap
        if 'mm' in info:
            self.mm = info['mm']
            if not(self.name in('hole','stair') and not self.world.quests['dungeon']):
                world.mms.add(self)

        # House
        if self.name == "house" and self.data:
            self.world.pnjs[self.data].house = self
        
    def save(self):
        data = ""
        if self.data:
            if isinstance(self.data, list):
                data = json.dumps(self.data)
            else:
                data = str(self.data)
            data = " " + data
        return f"{int(self.rect.x)} {int(self.rect.y)} {self.name} {self.map} {self.health.value}"+data
    
    def damage(self):
        if self.name == 'abandoned' and self.data != None: return
        
        if super().damage():
            sounds.hit.play()

    def die(self):
        sounds.lasthit.play()
        # Barn
        if self.name == 'abandoned' and self.data == None:
            # ruin image
            self.world.quests['abandoned'] = True
            self.data = "d"
            self.image = self.world.props_imgs['barn_destroy']
            # dont kill
            super().die(False)
            return
        # Die
        super().die()
    
    def interact(self):
        plr = self.world.player

        # Unveil hole/dungeon stair
        if self.name in ('hole','stair') and self.world.quests['dungeon'] and self.world.mms not in self.groups():
            self.world.mms.add(self)
        # End Boat
        if self.name == 'boat':
            if plr.has(1) and not self.world.ended:
                self.remove(self.world.interacts)
                sounds.boat.play()
                sounds.boat.fadeout(3000)
                plr.frozen = True
                self.world.timers['end'].activate()
            else:
                self.world.overlay.open_dialog([None, 'You shall not go back without the RUBY !', None])
        # Fruit Tree
        elif self.name == 'fruit_tree':
            sounds.collect.play()
            plr.additem(16, len(self.data[1]))
            self.data = ['water']
            self.remove(self.world.interacts)
        # Locked mine/ladder
        elif self.name in ('mine','ladder') and not plr.has(11):
            self.world.overlay.open_dialog([None, "It's locked...", None])
        # Locked hole
        elif self.name == "hole":
            if self.world.quests['dungeon']:
                self.world.teleport(self.name)
            else:
                self.world.overlay.open_dialog(['You', "I'm too scared to enter for now.\nI hear some noise inside...", None])
        # Teleport
        else:
            self.world.teleport(self.name)

    def draw(self):
        # Player behind
        old = self.plr_behind
        plr_hitbox = self.world.player.hitbox
        self.plr_behind = plr_hitbox.colliderect(self.rect) and (plr_hitbox.bottom <= self.hitbox.top)
        self.alpha_timer.activate_var(self.plr_behind, old)

        # Alpha (behind and damage)
        alpha = self.health.cooldown.percent() * (1-.3*self.alpha_timer.percent())
        self.image.set_alpha(255*alpha)

        # Draw
        super().draw()

        # Fruit tree
        if self.name == 'fruit_tree':
            # Tag
            tag = None
            if self.data[0] == 'water' and self.world.player.has(15):
                tag = self.world.overlay.items[15]
            elif self.data[0] == 'wait':
                tag = self.world.overlay.font.render(str(math.ceil(self.data[1])), False, UI[2])
            elif self.data[0] == 'fruit':
                img = self.world.overlay.items[16]
                for pos in self.data[1]:
                    self.world.display.blit(img, img.get_rect(center=self.draw_rect.topleft+pos))
            # tag draw
            if tag:
                r = tag.get_rect(midbottom=self.draw_rect.midtop+vec2(0, -4*SCALE))
                pg.draw.rect(self.world.display, UI[6], r.inflate(8,8))
                pg.draw.rect(self.world.display, UI[5], r.inflate(8,8), 4)
                self.world.display.blit(tag,r)
                
    def update(self, dt):
        super().update(dt)
        self.alpha_timer.update()

        # apples ready
        if self.name == 'fruit_tree' and self.data[0] == 'wait':
            self.data[1] -= dt
            if self.data[1] <= 0:
                self.add(self.world.interacts)
                self.data = ['fruit', [(
                    randint(0, 19)*SCALE,
                    randint(0, 21)*SCALE,
                
                ) for _ in range(randint(2,4))]]