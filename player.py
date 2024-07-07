import pygame as p
from inventory import Inventory
from sprite import Entity
from pebble import Pebble
from util import *

# !!!
# world overlay ...


class Player(Entity):
    def __init__(self, data, world):
        super().__init__(world, map=data.get('map',WILD), pos=data['pos'], anim=world.imgs['player'], hitbox=PLR_HITBOX)

        # Minimap
        self.add(world.mms)
        self.mm = 0

        # Some info
        self.spawn_pos = data.get('spawn_pos', self.pos_int)
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
        self.damage_imgs, self.water_img, self.break_img = [5],6,7

        # health
        self.health.max = 12
        self.health.value = data.get('health')
        self.health.cooldown.duration = 500

        self.timers['dead'] = Transition(1000, callmid=self.respawn)
        self.timers['knockback'] = Timer(500)

        # quests
        self.quests = data.get('quests', [])

        # timers
        self.timers['fishing'] = Timer(2000)
        self.timers['walk'] = Timer(400)

    def save(self):
        if self.dead:
            self.respawn()
            
        return {
            "pos": self.pos_save,
            "spawn_pos": self.spawn_pos,
            "inventory": self.inventory.save(),
            "tools": self.tools,
            "tool": self.tool,
            "map": self.map,
            "health": self.health.value,
            'quests': self.quests
        }

    @property
    def dead(self): return self.health.dead
    def unfreeze(self): self.frozen = False

    def input(self, keys, mouse, dt):
        # Reset direction (not keep moving if stopped!)
        self.movement.direction = vec2()

        # Dead or frozen: None
        if self.dead or self.frozen: return

        # DIRECTION
        self.format_direction(vec2(
            iskeys(keys,K_RIGHT)-iskeys(keys,K_LEFT),
            iskeys(keys,K_DOWN)-iskeys(keys,K_UP)
        ))

        # Fishing (mouse)
        if self.get_tool() == 8 and self.timers['tool'].active:
            # Stop player
            self.movement.direction = vec2()
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
        if self.dead: return
        # Tool
        if e.type == pg.MOUSEBUTTONDOWN and e.button == 1 and not self.timers['tool'].active and self.tools and self.world.overlay.cursor:
            self.use_tool()
    
    def damage(self, queen=False):
        if self.dead: return
        
        if super().damage():
            # FX
            sounds.plrhurt.play()
            self.world.scratch_pc.new(self.pos, anim=queen)
        
    def die(self):
        super().die(False)
        sounds.plrdead.play()

        self.timers['dead'].activate()
        self.status = 'dead'
        self.movement.direction = vec2()

    def respawn(self):
        """ Respawn player """

        self.pos = self.spawn_pos
        self.health.value = self.health.max

        # Timers reset + timer respawn fade
        for timer in self.timers.values():
            timer.deactivate()
        self.timers['dead'].activate(1)

        # Queen restore
        queen = self.world.queen
        if queen and queen.alive():
            # TP queen
            queen.pos = queen.spawn_pos
            # Regen queen
            if queen.health.value < queen.health.max:
                self.world.overlay.open_dialog([None, "The queen health was restored.", None])
                queen.health.value = queen.health.max
            
    def check_interact(self):
        if self.world.overlay.busy(): self.interact = None; return

        old = self.interact
        self.interact = None
        interact_dist = TS*2
        
        # PNJs
        for obj in self.world.filtered(self.world.pnjs.values()):
            if obj.name == 'explorer' and not self.world.ended and self.has(1):continue
            dist = obj.pos.distance_to(self.pos)
            if dist < interact_dist:
                self.interact = obj
                interact_dist = dist
            
        # Interact props
        for prop in self.world.filtered(self.world.interacts):
            dist = prop.pos.distance_to(self.pos)
            if dist < interact_dist:
                self.interact = prop
                interact_dist = dist

            # wider range for boat
            elif prop.name=='boat' and dist <= TS*3 and (self.interact==None or dist<interact_dist):
                self.interact = prop
                interact_dist = dist
        
        # Fadein interact ui
        self.timers['interact'].activate_var(self.interact, old)
    
    def use_tool(self):
        # Rotate player
        self.movement.side = ('L','R')[(self.world.mouse_pos.x-W/2)>0]
        
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
                Pebble(self, self.tool_draw[3], normalize(self.world.mouse_world_pos-self.tool_draw[3]), self.world.sprites)
        
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
                                particle=self.water_img,
                                floor=prop.rect.bottom,
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

    def anim_new(self):
        # Walk FX
        if self.status == 'move':
            idx = int(self.animation.frame_idx)
            if idx in(0,2):
                self.world.foot_pc.new(self.rect.topleft+vec2(7,14)*SCALE)
            elif idx == 3:
                choice((sounds.walk,sounds.walk_mines)[self.map != WILD]).play()

    def anim_end(self):
        # Onetime anims
        return self.status not in ('damage','dead')
            
    def update_tool_draw(self):
        tool = TOOLS[self.get_tool()]
        img = self.world.imgs['tools'][tool][SIDES.index(self.movement.side)]
        if self.movement.side == 'L':
            hand = self.rect.midleft+vec2(0,2)*SCALE
            rect = img.get_rect(midright=hand)
            spot = rect.midleft
        elif self.movement.side == 'R':
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
        # Dead
        if self.dead:
            self.animation.update(dt)
            return
        
        # Update
        self.check_interact()
        self.update_timers()
        self.animation.update(dt)
        self.health.update(dt)
        
        # Movement
        if self.timers['knockback'].active:
            self.movement.direction += self.timers['knockback'].dir * self.speed
        self.movement.update(dt, False)

        # Side
        if not self.timers['tool'].active and self.movement.direction.x:
            self.movement.side = 'LR'[self.movement.direction.x > 0]
        self.mm = self.movement.side == 'L'

        # Status
        if self.health.cooldown.active and not self.movement.moving:
            self.status = 'damage'
        else:
            self.status = ("idle","move")[self.movement.moving]

        # Fishing state
        if self.get_tool() == 8 and self.timers['tool'].active:
            if not self.timers['fishing'].active and proba(int(8/self.world.dt)):
                self.timers['fishing'].activate()
                sounds.bubbles.play()
                self.world.bubble_pc.new(self.tool_draw[3])
