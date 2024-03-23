import math
import pygame as pg
from inventory import Inventory
from sprites.entity import Entity
from sprites.pebble import Pebble
from util.support import *


class Player(Entity):
    def __init__(self, data, world, groups):
        super().__init__(world, data.get('map',WILD), data['pos'], groups, hitbox=CHAR_HB, side='R')
        
        self.mm = 0
        self.spawn_pos = data.get('spawn_pos', (int(self.pos.x),int(self.pos.y)))
        self.frozen = False

        # Interact
        self.interact = None
        self.timers['interact'] = Transition(200)
        
        # Inventory
        self.inventory = Inventory({int(i):a for i,a in data.get('inventory',{}).items()})
        
        # Tools
        self.tools = data.get("tools", [])
        self.tool = data.get('tool', 0)

        self.get_tool = lambda data=False: (self.tools[self.tool] if data else self.tools[self.tool][0]) if self.tools else None
        self.tool_draw = None
        self.timers['tool'] = Timer(300)
        self.hand = load("player/hand",scale=SCALE)

        # particles
        self.dmg_img,self.water_img,self.break_img = world.damage_imgs[5:8]
        self.particles = []

        # health
        self.max_health = 400
        self.health = data.get('health',self.max_health)
        self.timers['damage'] = Timer(500)
        self.timers['dead'] = Transition(1000, callmid=self.respawn)
        self.timers['knockback'] = Timer(500)

        # quests
        self.quests = data.get('quests', [])

        # Random timers
        self.timers['fishing'] = Timer(2000)
        self.timers['walk'] = Timer(400)
    
    def move(self, dt):
        # Normalize direction
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        
        if self.timers['knockback'].active:
            self.direction += self.timers['knockback'].direction
        
        # Apply movement
        self.hitbox.centerx += round(self.direction.x * self.speed * dt)
        self.collision("h")
        self.hitbox.centery += round(self.direction.y * self.speed * dt)
        self.collision("v")

        self.set_position()

    def load_graphics(self, _):
        size = (15*SCALE,24*SCALE)
        ts = load_tileset('player/player', size=size)
        
        self.shadows = {}
        animation = {}
        
        def anim(name, y):
            imgs_r = ts[y*4:(y+1)*4]
            for n, imgs in ((f"{name}_R",imgs_r),(f"{name}_L",flips(imgs_r,1))):
                anims, shadows = [],[]
                for img in imgs:
                    shadow, img = get_shadow(img, 8*SCALE)
                    shadows.append(shadow); anims.append(img)
                animation[n] = anims
                self.shadows[n] = shadows
                
        anim('idle',  0)
        anim("move",  1)
        anim("damage",2)
        anim("dead",  3)
        return animation
    
    def save(self):
        if self.status == 'dead':
            self.respawn()
            
        return {
            "pos": (int(self.pos.x),int(self.pos.y)),
            "spawn_pos": self.spawn_pos,
            "inventory": self.inventory.save(),
            "tools": self.tools,
            "tool": self.tool,
            "map": self.map,
            "health": self.health,
            'quests': self.quests
        }
    
    def get_side(self):
        super().get_side()
        self.mm = self.side == 'L'

    def unfreeze(self):
        self.frozen = False

    def input(self, keys, mouse, dt):
        # Reset direction (not keep moving if stopped!)
        old_dir = self.direction
        self.direction = vec2()

        # Dead or frozen: None
        if self.status == 'dead': return
        if self.frozen: return

        # DIRECTION
        self.direction.x = iskeys(keys,K_RIGHT) - iskeys(keys,K_LEFT)
        self.direction.y = iskeys(keys,K_DOWN) - iskeys(keys,K_UP)
        
        # Fishing (mouse)
        if self.get_tool() == 8 and self.timers['tool'].active:
            # Stop player
            self.direction = vec2()
            # Continue using rod
            if mouse[0]:
                self.timers['tool'].activate()
            # Release
            else:
                self.timers['tool'].deactivate()
                # If there was a fish
                if self.timers['fishing'].active:
                    self.additem(9)
                    sounds.fish.play()
                    for _ in range(4):
                        self.damage_pc(self.water_img)
                self.timers['fishing'].deactivate()

    def event(self, e):
        if self.status == 'dead': return

        # Interact
        if self.interact:
            o = self.world.overlay
            if e.type == pg.KEYDOWN and e.key == pg.K_SPACE:
                sounds.press.play()
                o.interact_press.activate()
            elif e.type == pg.KEYUP and e.key == pg.K_SPACE:
                sounds.release.play()
                o.interact_press.callback()
                o.interact_press.deactivate()
    
        # Tool
        if e.type == pg.MOUSEBUTTONDOWN and e.button == 1 and not self.timers['tool'].active and self.tools and self.world.overlay.cursor:
            self.use_tool()
    
    def damage(self, queen=False):
        if self.timers['dead'].active: return
        if self.timers['damage'].active: return
        self.timers['damage'].activate()
        self.health -= 1
        sounds.plrhurt.play()

        for _ in range(self.health):
            self.damage_pc()
        self.world.scratch_pc.new(self.pos, anim=queen)
        
        if self.health <= 0:
            self.health = 0

            for _ in range(self.max_health):
                self.damage_pc()

            self.timers['dead'].activate()
            self.status = 'dead'
            self.frame_idx = 0
            self.direction = vec2()

            sounds.plrdead.play()

    def respawn(self):
        """ Respawn player """
        self.status = "idle"
        if self.health > 0: return

        # Data
        self.set_position(self.spawn_pos)
        self.health = self.max_health
        self.side = "R"
        self.frame_idx = 0
        self.inventory.selected_idx = 0

        # Timers reset + timer respawn fade
        for timer in self.timers.values():
            timer.deactivate()
        self.timers['dead'].activate(1)

        # Queen health regen
        if self.world.queen and self.world.queen.alive():
            self.world.queen.set_position(self.world.queen.spawn_pos)
            if self.world.queen.health < self.world.queen.max_health:
                self.world.overlay.open_dialog([None, "The queen health was restored.", None])
                self.world.queen.health = self.world.queen.max_health
            
    def check_interact(self):
        old = self.interact
        self.interact = None
        inter_dist = None
        if self.world.overlay.busy(): return
        
        # PNJs
        for pnj in self.world.filtered(self.world.pnjs.values()):
            if pnj.name == 'explorer' and not self.world.ended and self.has(1):continue
            dist = pnj.pos.distance_to(self.pos)
            if dist <= TS*2 and not(inter_dist!=None and dist>inter_dist):
                self.interact = pnj
                inter_dist = dist
            
        # Interact props
        for prop in self.world.filtered(self.world.interacts):
            dist = prop.pos.distance_to(self.pos)
            if dist <= TS*2 and not(inter_dist!=None and dist>inter_dist):
                self.interact = prop
                inter_dist = dist

            # wider range for boat
            elif prop.name=='boat' and dist <= TS*3 and not(inter_dist!=None and dist>inter_dist):
                self.interact = prop
                inter_dist = dist
        
        # Fadein interact ui
        self.timers['interact'].activate_var(self.interact, old)
    
    def use_tool(self):
        # Rotate player
        self.side = ('L','R')[(self.world.mouse_pos.x-W/2)>0]
                
        # Broken
        if self.get_tool(1)[1] == 0 and self.get_tool()!=15:
            sounds.broken.play()
            return
        
        # Timer
        self.timers['tool'].activate()

        self.update_tool_draw()

        # Tool function
        used = False
                   
        # Attack
        if self.get_tool() in TOOL_ATTACK:
            damage, duration = TOOL_ATTACK[self.get_tool()]
            self.timers['tool'].duration = 300*duration
            for animal in self.world.filtered(self.world.animals_queen):
                if animal.rect.colliderect(self.tool_draw[1]):
                    animal.damage(damage)
                    used = True

        # Water (fishing)
        if self.get_tool() == 8:
            for water in self.world.filtered(self.world.waters):
                if water.hitbox.collidepoint(self.tool_draw[3]):
                    sounds.fishing.play()
                    used = True
                    break
            else:
                self.timers['tool'].deactivate()

        # Lance
        elif self.get_tool() == 5:
            sounds.sword.play()

        # Slingshot (throw stone):
        elif self.get_tool() == 14:
            sounds.slingshot.play()
            if self.has(2):
                self.removeitem(2)
                Pebble(self, self.tool_draw[3], (self.world.mouse_world_pos-self.tool_draw[3]).normalize(), self.world.sprites)
        
        # Watering can:
        elif self.get_tool() == 15:
            # Fruit trees
            if self.get_tool(1)[1]:
                for prop in self.world.props_filter:
                    if prop.name == "fruit_tree" and prop.data[0]=='water' and prop.rect.colliderect(self.tool_draw[1]):
                        sounds.water.play()
                        for _ in range(8):
                            self.world.damage_pc.new(
                                vec2(self.tool_draw[3]),
                                image=self.water_img.copy(),
                                floor=prop.rect.bottom,
                                #group=self.particles
                            )
                        prop.data = ['wait', FRUITTREE_TIME]
                        self.get_tool(1)[1] -= 1
                        break
            # Fill can
            else:
                for water in self.world.filtered(self.world.waters):
                    if water.hitbox.colliderect(self.tool_draw[1]):
                        sounds.fishing.play()
                        self.get_tool(1)[1] = TOOL_DURA[15]
                        for _ in range(4):
                            self.damage_pc(self.water_img)
                        break

        # Props (break)
        else:
            for prop in self.world.props_filter:
                if prop.tool == self.get_tool():
                    if prop.rect.colliderect(self.tool_draw[1]):
                        prop.damage()
                        used = True
                
                # hammer: range damage
                elif self.get_tool() == 13 and prop.tool == 4:
                    if prop.pos.distance_to(self.tool_draw[3]) < HAMMER_RANGE:
                        prop.damage()
                        used = True

            # Sounds
            match self.get_tool():
                case 13:
                    sounds.hammer.play()
                    self.world.hammer_pc.new(self.tool_draw[3])
                case 3:
                    sounds.axe.set_volume(.5-.1*used)
                    sounds.axe.play()
                case 4: sounds.pickaxe.play()

        # Damage tool
        tool = self.get_tool(1)
        if used and tool[1] > 0:
            tool[1] -= 1
            if tool[1] == 0:
                for _ in range(4):
                    self.damage_pc(self.break_img)
                sounds.broken.play()

    def additem(self, item, amount=1):
        if item in TOOLS:
            for _ in range(amount):
                self.tools.append([item, TOOL_DURA[item]])
        else:
            self.inventory.add(item, amount)

        # End
        if item == 1 and not self.world.ended:
            self.world.overlay.panel = None
            self.world.overlay.open_dialog(
                [None,'You made it. You got the ruby.',None],
                [None,'Your journey ends here.',None],
                [None,'Say goodbye to the hamlet,\ngo to the boat,\nand leave.',None],
            )

    def has(self, i1, a1=1):
        if i1 in TOOLS:
            return len(list(filter(lambda its:its[0]==i1, self.tools))) >= a1
        else:
            return self.inventory.has(i1,a1)
    
    def removeitem(self, i1, a1=1):
        if i1 in TOOLS:
            # Tool idx
            self.tool = 0
            # Loop tools
            for its in self.tools:
                if its[0]==i1:
                    # Remove tool
                    self.tools.remove(its)
                    # Reduce amount
                    a1 -= 1
                    if a1 == 0:
                        break
        else:
            self.inventory.remove(i1,a1)
        self.world.overlay.inv_idx = 0

    def get_status(self):
        super().get_status()
        if self.status == 'idle' and self.timers['damage'].active:
            self.status = 'damage'

    def animate(self,dt):
        old = int(self.frame_idx)
        if self.status in ("damage","dead"):
            length = len(self.animation[self.status+'_'+self.side])
            if self.frame_idx+(ANIM_SPEED * dt) >= length:
                return
        
        super().animate(dt)

        # New frame
        idx = int(self.frame_idx)
        if old != idx:
            # Particles, sound
            if self.status == 'move':
                if idx in(0,2):
                    self.world.foot_pc.new(self.rect.topleft+vec2(7,14)*SCALE)
                elif idx == 3:
                    choice((sounds.walk,sounds.walk_mines)[self.map != WILD]).play()

    def update_fishing(self):
        if not self.timers['fishing'].active and proba(int(8/self.world.dt)):
            self.timers['fishing'].activate()
            sounds.bubbles.play()
            self.world.bubble_pc.new(self.tool_draw[3])

    def update_tool_draw(self):
        tool = TOOLS[self.get_tool()]
        img = self.world.tools[tool][SIDES.index(self.side)]
        if self.side == 'L':
            hand = self.rect.midleft+vec2(0,2)*SCALE
            rect = img.get_rect(midright=hand)
            spot = rect.midleft
        elif self.side == 'R':
            hand = self.rect.midright+vec2(0,2)*SCALE
            rect = img.get_rect(midleft=hand)
            spot = rect.midright
        self.tool_draw = (img, rect, hand, spot)
        
    def draw(self):
        super().draw()
        if self.timers['tool'].active:
            self.update_tool_draw()
            self.world.display.blit(self.tool_draw[0], self.tool_draw[1].move(-self.world.offset))
            self.world.display.blit(self.hand, self.hand.get_rect(center=self.tool_draw[2]-self.world.offset))

    def update(self, dt):
        self.update_timers()
        
        if self.status == "dead":
            res = self.animate(dt)
            return
        
        self.check_interact()
        if not self.timers['tool'].active:
            self.get_side()
        self.get_status()
        self.animate(dt)
        self.move(dt)

        if self.get_tool() == 8 and self.timers['tool'].active:
            self.update_fishing()