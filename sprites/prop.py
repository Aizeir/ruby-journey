from sprites.sprite import Sprite
from util.prop_data import PROP_DATA
from util.support import *

class Prop(Sprite):
    def __init__(self, data, world, groups, setpos=False):
        """ Data: deja split """

        # Name & Animation
        self.name = data[2]
        info = PROP_DATA[self.name]
        anim_name = self.name if self.name!='tree' else choice(('tree','tree2'))
        anim = world.props_imgs[anim_name]

        super().__init__(world, data[3], (int(data[0]),int(data[1])), anim, groups, info['hitbox'])
        
        # Shadow
        if 'shadow' in info:
            shadows = world.shadow_imgs[anim_name]
            if isinstance(shadows, dict):
                self.shadows = shadows
            else:
                self.shadow = shadows

        # Center pos
        if setpos: self.set_position(self.rect.topleft)
        
        # Info
        self.drop = info.get('drop')
        self.tool = info.get('tool')
        
        # Damage
        self.dmg_imgs = [world.damage_imgs[x] for x in info.get('damage',[0])]
        self.max_health = info.get('health', 1)
        self.health = int(data[4]) if data[4] else self.max_health
        self.damage_timer = Timer(500)

        # Alpha
        self.alpha_timer = Transition(200, 100)
        self.behind = False

        # Data
        self.data = data[5] if len(data)>5 else None

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

    def save(self):
        data = ""
        if self.data:
            if isinstance(self.data, list): data = json.dumps(self.data)
            else: data = str(self.data)
            data = " "+data
        return f"{int(self.pos.x)} {int(self.pos.y)} {self.name} {self.map} {self.health}"+data

    def set_position(self, pos=None):
        """ Set position (regardless collisions). """
        self.hitbox.center = pos or self.hitbox.center
        self.rect.midbottom = self.hitbox.midbottom
        self.pos = vec2(self.hitbox.center)

    def damage_pc(self):
        self.world.damage_pc.new(
            vec2(randint(self.rect.x,self.rect.right),randint(self.rect.y,self.rect.bottom)),
            image=choice(self.dmg_imgs).copy(),
            floor=self.rect.bottom,
            #group=self.particles
        )
    
    def damage(self):
        if self.name == 'abandoned' and self.data != None: return
        self.health -= 1
        self.damage_timer.activate()
        sounds.hit.play()

        for _ in range(self.health): self.damage_pc()

        if self.health == 0:
            for _ in range(self.max_health): self.damage_pc()
            sounds.lasthit.play()
            if self.drop:
                self.world.player.additem(*self.drop)
            if self.name == 'abandoned' and self.data == None:
                self.world.quests['abandoned'] = True
                self.data = "d"
                self.image = self.world.props_imgs['barn_destroy']
                return
            self.kill()
    
    def interact(self):
        plr = self.world.player
        # Unveil props
        if self.name in ('hole','stair') and self.world.quests['dungeon'] and self.world.mms not in self.groups():
            self.world.mms.add(self)

        # Interact
        if self.name == 'boat':
            if plr.has(1) and not self.world.ended:
                self.remove(self.world.interacts)
                sounds.boat.play()
                sounds.boat.fadeout(3000)
                plr.frozen = True
                self.world.timers['end'].activate()
            else:
                self.world.overlay.open_dialog([None, 'You shall not go back without the RUBY !', None])
        
        elif self.name == 'fruit_tree':
            sounds.collect.play()
            plr.additem(16, len(self.data[1]))
            self.data = ['water']
            self.remove(self.world.interacts)
        
        elif self.name in ('mine','ladder') and not plr.has(11):
            self.world.overlay.open_dialog([None, "It's locked...", None])
        elif self.name == "hole":
            if self.world.quests['dungeon']:
                self.world.teleport(self.name)
            else:
                self.world.overlay.open_dialog(['You', "I'm too scared to enter for now.\nI hear some noise inside...", None])
        else:
            self.world.teleport(self.name)

    def draw(self):
        # Rect
        display, rect = self.world.display, self.rect.move(-self.world.offset)

        # behind
        old = self.behind
        plr_hitbox = self.world.player.hitbox
        self.behind = plr_hitbox.colliderect(self.rect) and (plr_hitbox.bottom <= self.hitbox.top)
        self.alpha_timer.activate_var(self.behind, old)

        # alpha
        alpha = self.damage_timer.percent() * (1-.3*self.alpha_timer.percent())
        self.image.set_alpha(255*alpha)
        if self.shadow: self.shadow.set_alpha(255*alpha)
        
        # Health
        if self.damage_timer.active:
            surf = pg.Surface((24,12))
            surf.set_alpha((1-self.damage_timer.percent())*255)
            surf.fill("#734d5c")
            pg.draw.rect(surf, '#a76772', (0,0,surf.get_width()*self.health/self.max_health,surf.get_height()))
            display.blit(surf, surf.get_rect(midbottom=rect.midtop+vec2(0,-4)))
        
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
                    display.blit(img, img.get_rect(center=rect.topleft+pos))

            if tag:
                r = tag.get_rect(midbottom=rect.midtop+vec2(0, -4*SCALE))
                pg.draw.rect(display, UI[6], r.inflate(8,8))
                pg.draw.rect(display, UI[5], r.inflate(8,8), 4)
                display.blit(tag,r)
                
    def update(self, dt):
        self.damage_timer.update()
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

        return super().update(dt)