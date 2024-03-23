from math import sin
import math
from random import choices
import time
from pytmx.util_pygame import load_pygame
from overlay import Overlay
from player import Player
from sprites.animal import Animal
from sprites.pnj import PNJ
from sprites.prop import Prop
from sprites.queen import Queen
from sprites.sprite import Sprite
from util.pnj_data import PNJ_IDX
from util.prop_data import PROP_DATA
from util.support import *
import particle

class World:
    def __init__(self, game, world_data):
        self.game = game
        self.display = game.display
        self.offset = vec2(0,0)
        self.paused = False 
        self.timers = {}
        self.new = not world_data

        # Day night
        self.daydura = 60
        self.daynight = self._daynight_compute()

        # cutscene
        self.cutscene = None

        # Mouse pos
        self.mouse_pos = pg.mouse.get_pos()
        self.mouse_world_pos = vec2()

        # Tools
        self.tools = {n: [x,pg.transform.rotate(pg.transform.flip(x,1,0), 180),pg.transform.rotate(x, -90),pg.transform.rotate(pg.transform.flip(x,1,0), 90)] for n,x in load_folder_dict("tools", load, SCALE).items()}

        # Sprites
        self.sprites = pg.sprite.Group()
        self.collides = pg.sprite.Group()
        self.all_collide = (self.sprites, self.collides)
        self.props = pg.sprite.Group()
        self.stones = pg.sprite.Group()
        self.waters = pg.sprite.Group()
        self.animals = pg.sprite.Group()
        self.animals_queen = pg.sprite.Group()
        self.interacts = pg.sprite.Group()
        self.mms = pg.sprite.Group()
        self.apnjs = (self.all_collide, self.mms)
        self.aprops = (self.all_collide, self.props)
        self.aanimals = (self.all_collide, self.animals, self.animals_queen)
        self.pnjs = {}
        # - optimization
        self.collides_filter = ()
        self.props_filter = ()

        # Quests
        self.quests = world_data.get('quests', {
            "abandoned": False,
            "queen": False,
            "dungeon": False,
            "mines": False
        })

        # End
        self.ended = world_data.get('ended',False)
        def callend(): self.player.frozen = False
        self.timers['end'] = Transition(1000,callmid=self.end,callend=callend)

        # Images
        self.pnj_imgs = load_folder_dict('pnj', load_tileset, (15*SCALE,24*SCALE))
        self.queen_imgs = load_tileset("animal/queen", (64*SCALE,70*SCALE))
        self.animal_imgs = {
            'chicken':load_tileset("animal/chicken", (16*SCALE,18*SCALE)),
            'racoon':load_tileset("animal/racoon", (16*SCALE,18*SCALE))
        }
        # - props
        house_imgs = load_tileset("props/house", (44*SCALE,50*SCALE))
        boat_imgs = load_tileset("props/boat", (56*SCALE,32*SCALE))
        self.props_imgs = load_folder_dict("props", load, SCALE)
        self.props_imgs |= {
            'house':{
                None: [house_imgs[0]],
                "open": house_imgs,
                "close": list(reversed(house_imgs))
            },
            'mine':{None:load_tileset("props/mine", (38*SCALE,52*SCALE))},
            'torch':{None:load_tileset("props/torch", (5*SCALE,13*SCALE))},
            'campfire':{None:load_tileset("props/campfire", (12*SCALE,13*SCALE))},
            'boat':{None:boat_imgs[:2]},
            'boatpnj':boat_imgs[2],
            'boatpnj2':boat_imgs[3],
            'boatminer':{None:boat_imgs[4:6]},
        }

        # shadow
        self.shadow_imgs = {}
        for name, anim in self.props_imgs.items():
            if name not in PROP_DATA: continue
            if "shadow" not in PROP_DATA[name]: continue

            shadow_h = PROP_DATA[name]["shadow"]
            if isinstance(anim, pg.Surface):
                self.shadow_imgs[name], self.props_imgs[name] = get_shadow(anim, shadow_h)
            elif isinstance(anim, list):
                self.shadow_imgs[name] = []
                self.props_imgs[name] = []
                for img in anim:
                    shadow, img = get_shadow(img, shadow_h)
                    self.shadow_imgs[name].append(shadow)
                    self.props_imgs[name].append(img)
            elif isinstance(anim, dict):
                self.shadow_imgs[name] = {}
                self.props_imgs[name] = {}
                for status, imgs in anim.items():
                    self.shadow_imgs[name][status] = []
                    self.props_imgs[name][status] = []
                    for img in imgs:
                        shadow, img = get_shadow(img, shadow_h)
                        self.shadow_imgs[name][status].append(shadow)
                        self.props_imgs[name][status].append(img)

        # - details
        details_imgs = load_tileset("tilesets/details")
        self.details_imgs = [details_imgs[:len(details_imgs)//2],details_imgs[len(details_imgs)//2:]]
        self.mine_details_imgs = load_tileset("tilesets/mine_details")
        self.water_imgs = load_tileset("tilesets/water")
        self.water_imgs = [self.water_imgs, flips(self.water_imgs,1)]
        # - other
        self.pebble_img = load("particle/stone",scale=SCALE)
        self.scratch_imgs = [
            load_tileset("particle/scratch", scale=SCALE),
            load_tileset("particle/scratch_queen", size=(TS*2,TS*2), scale=SCALE)
        ]

        # Masks
        self.light_mask = load("particle/torch_mask",size=TILE*6)
        self.queen_mask = load(self.light_mask,scale=4)

        # Particles
        gravity = 40
        # - bubble
        bubble = load('particle/bubble', scale=SCALE)
        self.bubble_pc = particle.Particle(size=4)
        self.bubble_pc.draw(particle.draw_image)
        @self.bubble_pc.update
        def update(p,w):
            p['size'] += 1.5
            if p['size'] > bubble.get_width():
                self.bubble_pc.delete(p)
                self.player.timers['fishing'].deactivate()
            else:
                p['image'] = pg.transform.scale(bubble, (p['size'],p['size']))
                p['image'].set_alpha(255*(1-(p['size']/bubble.get_width())**2))
        # - damage
        self.damage_imgs = load_tileset('tilesets/damage', (4*SCALE,4*SCALE))
        self.damage_pc = particle.Particle()
        self.damage_pc.init(lambda p,**k: {"direction":vec2(randint(-200,200), -4)}|k)
        self.damage_pc.draw(particle.draw_image)
        @self.damage_pc.update
        def update(p,w):
            if p['pos'].y > p['floor']:
                self.damage_pc.delete(p)
                return
            alpha = min((p['floor']-p['pos'].y)*6,255)
            p['image'] = pg.transform.scale(p['image'], (4*SCALE*alpha/255,4*SCALE*alpha/255))
            p['image'].set_alpha(alpha)
            p['direction'].y += gravity
            p['pos'] += p['direction']*self.dt
        # - scratch
        self.scratch_pc = particle.Particle()
        self.scratch_pc.draw(particle.draw_image)
        @self.scratch_pc.init
        def init(p,**k):
            return {
                "anim": self.scratch_imgs[k['anim']],
                'frame': 0,
                "image": self.scratch_imgs[k['anim']][0]
            }
        @self.scratch_pc.update
        def update(p,w):
            p['frame'] += ANIM_SPEED * self.dt
            if p['frame'] > len(p['anim'])-1:
                self.scratch_pc.delete(p)
            else:
                p['image'] = p['anim'][int(p['frame'])]
        # - hammer
        self.hammer_pc = particle.Particle()
        self.hammer_pc.init(lambda p,**k: {"size": HAMMER_RANGE})
        @self.hammer_pc.draw
        def draw(p,w):
            s = int(p['size'])
            x = 100*s//TS
            img = pg.Surface((s,s))
            pg.draw.circle(img, (x,x,x), (s//2,s//2), s//2)
            self.display.blit(img, img.get_rect(center=p['pos']-self.offset), special_flags=pg.BLEND_RGB_ADD)
        @self.hammer_pc.update
        def update(p,w):
            p['size'] /= 1.1
            if p['size'] <= 2:
                self.hammer_pc.delete(p)
        # - footprint
        foot = load('particle/foot', scale=SCALE)
        self.foot_pc = particle.Particle(dura=600)
        self.foot_pc.init(lambda p,**k: {'image': foot.copy()})
        self.foot_pc.draw(lambda p,w:self.display.blit(p['image'],p['pos']-self.offset))
        @self.foot_pc.update
        def update(p,w):
            t = pg.time.get_ticks()
            if (t-p['time'])>=p['dura']:
                self.foot_pc.delete(p)
                return
            x = (1-(t-p['time'])/p['dura'])**.5
            p['image'].set_alpha(255*x)
        
        # Floors
        self.floor_colors = {WILD:"#4a787b", MINES:(89,82,70), DUNGEON:"#333333"}
        self.floors = {
            WILD:load("map/map", scale=SCALE),
            MINES:load("map/mines", scale=SCALE),
            DUNGEON:load("map/dungeon", scale=SCALE),
        }
        self.water_pcs = []
        self.water_pcs_idx = 0

        # Minimap
        self.floors_mm = {m:pg.Surface(vec2(surf.get_size())//MMSCALE) for m,surf in self.floors.items()}
        self.mm = load_tileset("tilesets/minimap", scale=MM//4, size=(MM,MM))
        self.mm2 = load_tileset("tilesets/minimap2", size=(15*2,10*2), scale=2)

        # Data
        self.teleport_pos = {}

        # Maps
        wild_map = load_pygame("assets/map/map.tmx")
        mines_map = load_pygame("assets/map/mines.tmx")
        dung_map = load_pygame("assets/map/dungeon.tmx")
        maps = (wild_map,mines_map,dung_map)

        # COMMON
        # - Water (Wild)
        floor = wild_map.get_layer_by_name('floor')
        for x,y,img in floor.tiles():
            data = wild_map.get_tile_properties(x,y,wild_map.layers.index(floor))
            if not data: continue
            if 'hitbox' in data:
                hitbox = pg.Rect([int(x)*SCALE for x in data['hitbox'].split(" ")])
                Sprite(self, WILD, (x*TS,y*TS), img, (self.collides, self.waters), hitbox)
            if 'water' in data and proba(3):
                self.water_pcs.append((randint(0,1), x*TS,y*TS))
                
        # - Stone (mine/dungeon)
        for m, map in ((MINES,mines_map), (DUNGEON,dung_map)):
            floor = map.get_layer_by_name("floor")
            for x,y,img in floor.tiles():
                data = map.get_tile_properties(x,y,map.layers.index(floor))
                if not(data and "hitbox" in data): continue
                if data['hitbox']==1: hitbox = (TS, TS/2)
                elif data['hitbox']==2: hitbox = pg.Rect(0,0,TS,TS*2)
                else: hitbox = TILE
                Sprite(self, m, (x*TS,y*TS), load(img,scale=SCALE), (self.all_collide,self.stones), hitbox)
            
        # EXISTING WORLD
        if world_data:
            self.player = Player(world_data['player'], self, (self.all_collide,self.mms))
            self.queen = None
            if 'queen' in world_data:
                self.queen = Queen(world_data['queen'], self, (self.all_collide,self.animals_queen))
            for data in world_data['pnj']:
                PNJ(data, self, self.apnjs)
            for data in world_data['animal']:
                Animal(data, self, self.aanimals)
            for data in world_data['prop']:
                if DUNGEON in data and 'stone' in data: continue
                Prop(data.split(" "), self, self.aprops, True)

        # NEW WORLD
        else:
            for m, map in zip(MAPS,maps):
                # - Characters
                for obj in map.get_layer_by_name("characters"):
                    pos = (obj.x*SCALE,obj.y*SCALE)
                    # Player (its new world)
                    if obj.name == "player":
                        self.player = Player({"pos":pos}, self, (self.all_collide,self.mms))
                    # Queen
                    elif obj.name == "queen":
                        self.queen = Queen({'pos':pos}, self, self.all_collide)
                    # PNJ
                    elif obj.name in PNJ_IDX and not world_data:
                        PNJ({"name":obj.name, "pos":pos, 'map':m}, self, self.apnjs)

                # - Props
                for obj in map.get_layer_by_name("props"):
                    data = [obj.x*SCALE, obj.y*SCALE, obj.properties['name'], m, None]
                                   
                    # pnj house
                    if data[2] == 'house' and obj.name: data.append(obj.name.split(" ")[0])

                    Prop(data, self, self.aprops)
     
                # - Random generation
                i = map.layers.index(map.get_layer_by_name('floor'))
                for y in range(map.height):
                    for x in range(map.width):
                        # Check if floor tile (not path...)
                        data = map.get_tile_properties(x,y,i)
                        if not(data and "floor" in data): continue
                        
                        pos = (x*TS+randint(PROP_MARGIN,TS-PROP_MARGIN),y*TS+randint(PROP_MARGIN,TS-PROP_MARGIN))
                        # WILD GEN
                        if m == WILD: 
                            r = randint(1, 100 - 40*data['floor'])
                            # Tree
                            if r <= 10:
                                Prop((*pos, 'tree', m, None), self, self.aprops, True)
                            # Stone
                            elif r <= 11:
                                Prop((*pos, 'stone', m, None), self, self.aprops, True)
                            # Chicken
                            elif r <= 12:
                                Animal((pos, 'chicken', choice(('L','R')), m, None), self, self.aanimals)
                            # Torch
                            elif r <= 13:
                                Prop((*pos, 'torch', m, None), self, self.aprops, True)
                        
                        # MINES GEN
                        elif m == MINES: 
                            r = randint(1, 100)
                            # Stone
                            if r <= 20:
                                Prop((*pos, choices(('stone','stone_2','stone_big'),(4,2,1))[0], m, None), self, self.aprops, True)
                            # Racoon
                            elif r <= 21:
                                Animal((pos, 'racoon', choice(('L','R')), m, None), self, self.aanimals)
                            # Torch
                            elif r <= 22:
                                Prop((*pos, 'torch', m, None), self, self.aprops, True)
                        
                        # DUNGEON GEN
                        elif m == DUNGEON: 
                            r = randint(1, 100)
                            if r <= 4:
                                Prop((*pos, 'iron', m, None), self, self.aprops, True)
                            # Racoon
                            elif r <= 7:
                                Animal((pos, 'racoon', choice(('L','R')), m, None), self, self.aanimals)
                            # Torch
                            elif r <= 8:
                                Prop((*pos, 'torch', m, None), self, self.aprops, True)
                            # Big stone
                            elif r <= 9:
                                Prop((*pos, 'stone_big', m, None), self, self.aprops, True)
                            
        # Details
        for m, map in zip(MAPS,maps):
            i = map.layers.index(map.get_layer_by_name('floor'))
            for y in range(map.height):
                for x in range(map.width):
                    data = map.get_tile_properties(x,y,i)
                    if not data: continue

                    # Minimap
                    if 'minimap' in data:
                        self.floors_mm[m].blit(self.mm[data['minimap']], (x*MM,y*MM))

                    # Check if floor tile (not path...)
                    if "floor" not in data: continue
                    if proba(2):
                        # Detail
                        pos = (x*TS,y*TS)
                        imgs = [self.details_imgs[data['floor']], self.mine_details_imgs][m != WILD]
                        self.floors[m].blit(choice(imgs),pos)

        # Maps
        self.timers['map'] = Transition(1000, callmid=self.teleport_mid)
        self.timers['begin'] = Transition(1000)

        # Overlay
        self.overlay = Overlay(self)

    def save(self):
        data = {
            "ended": self.ended,
            "quests":self.quests,
            "player":self.player.save(),
            "pnj": [pnj.save() for pnj in self.pnjs.values()],
            "prop": [prop.save() for prop in self.props],
            "animal": [animal.save() for animal in self.animals],
        }
        if self.queen and self.queen.alive():
            data["queen"] = self.queen.save()
        return data


    def open(self):
        self.timers['begin'].activate(1)
        self.play_music()

        # Debut
        if self.new:
            def callback():
                self.new = False
                self.player.additem(0)
                self.overlay.open_dialog(
                    [None, "You arrived.", None],
                    [None, f"Follow the tutorial ?", {
                    "Yes": self.tutorial,
                    "No": None
                }])
            
            self.compute_offset()
            self.offset += vec2(0,TS*5)
            self.cutscene = (vec2(self.player.rect.center), callback)
            pg.mixer.music.stop()

    def tutorial(self):
        return[
            [None,"WASD or ZQSD or arrows\nto move.",None],
            [None,"ESC to pause.",None],
            [None,"Scroll to navigate\nthrough inventory items.",None],
            [None,"Click to use tool.\nTAB to switch tool.\nThere are 6 types in total.",None],
            [None,"The game is automatically saved\nwhen you quit.",None],
            [None,"Chat with local NPCs and do their quests\nto unlock their trades.",None],
            [None,"At the beginning, try to get\na tool as fast as possible.",None],
            [None,"You can repair your current tool\nat the blacksmith.",None],
            [None,"A cozy game in a cozy village.\nMake money and get the ruby.",None],
            [None,"Good luck !",None],
        ]

    def play_music(self):
        #return# !!!
        if self.player.map == WILD:
            if self.daynight <= 128:
                music("music.wav", -1, .7, fade_ms=self.timers['map'].duration)
                sounds.ambiance.play(-1, fade_ms=self.timers['map'].duration)
            else:
                music("night.wav", -1, .7, fade_ms=self.timers['map'].duration)
                sounds.crickets.play(-1, fade_ms=self.timers['map'].duration)
                sounds.wind.play(-1, fade_ms=self.timers['map'].duration)

        elif self.player.map == MINES:
            music("cave.wav", -1, .5, fade_ms=self.timers['map'].duration)
            sounds.wind.play(-1, fade_ms=self.timers['map'].duration)
        elif self.player.map == DUNGEON:
            music("dungeon.wav", -1, .5, fade_ms=self.timers['map'].duration)

    def end(self):
        self.ended = True
        self.game.scene = self.game.mainmenu
        self.game.mainmenu.play_music()
        self.game.mainmenu.end.activate()
        self.game.mainmenu.menu = 'end'

    def teleport(self, enter):
        self.timers['map'].exit = PROP_DATA[enter]['teleport']
        self.timers['map'].activate()

        pg.mixer.music.fadeout(self.timers['map'].duration)
        sounds.ambiance.fadeout(self.timers['map'].duration)
        sounds.crickets.fadeout(self.timers['map'].duration)
        sounds.wind.fadeout(self.timers['map'].duration)

        # Enter sound
        if enter == "mine":
            sounds.mines_enter.play()
        elif ("ladder"in enter) or (enter=='hole'):
            sounds.ladder.play()
        elif 'stair' in enter:
            sounds.stair.play(fade_ms=200)

    def teleport_mid(self):
        exit = self.timers['map'].exit
        map, pos = self.teleport_pos[exit]

        self.player.map = map
        self.player.set_position(pos)
        self.player.spawn_pos = (int(pos.x),int(pos.y))
        
        self.timers['map'].activate(1)
        self.play_music()

        # Exit sound
        if exit == "mine":
            sounds.mines_exit.play()
        elif ("ladder"in exit) or (exit=='hole'):
            sounds.ladder.play()
        elif 'stair' in exit:
            sounds.stair.fadeout(200)
        
        # dungeon cutscene
        if self.player.map == "dungeon" and not self.quests['dungeon']:
            pnj = self.pnjs["miner"]

            def callback():
                self.quests['dungeon'] = 1
                pnj.talk()
            self.compute_offset()
            self.cutscene = (vec2(pnj.rect.center), callback)
            pg.mixer.music.stop()

        # mines cutscene
        elif self.player.map == "mines" and not self.quests['mines']:
            def callback():
                self.quests['mines'] = True
            self.compute_offset()
            self.cutscene = (self.player.pos+vec2(0,TS*3), callback)
            pg.mixer.music.stop()

    def event(self, e):
        if self.cutscene: return
        if not self.paused and not self.overlay.busy():
            self.player.event(e)
        self.overlay.event(e)

    def input(self, dt):
        self.mouse_world_pos = self.mouse_pos + self.offset
        k = pg.key.get_pressed()
        m = pg.mouse.get_pressed()

        self.overlay.input(k, m, dt)
        self.player.input(k, m, dt)
    
    def compute_offset(self):
        self.offset.x = self.player.rect.centerx - W/2
        self.offset.y = self.player.rect.centery - H/2

    def update_cutscene(self):
        center = vec2(W/2,H/2)
        self.offset += (self.cutscene[0] - center - self.offset) / 80
        # End
        if (center+self.offset).distance_to(self.cutscene[0]) < TS//4:
            self.play_music()
            self.cutscene[1]()
            self.cutscene = None

    def _daynight_compute(self):
        t = sin((pg.time.get_ticks() / (self.daydura*1000) + 1)*math.pi)
        return math.e**(8*t)/(1+math.e**(8*t)) * 255

    def update_daynight(self):
        x = self._daynight_compute()
        self.display.fill((0,x*1/8,x*2/8), special_flags=pg.BLEND_RGB_SUB)
        fade = 3000
        
        # Transition
        if x>=15>=self.daynight or x<=240<=self.daynight:
            pg.mixer.music.fadeout(fade)
            sounds.ambiance.fadeout(fade)
            sounds.crickets.fadeout(fade)
            sounds.wind.fadeout(fade)
        # Sunset (x est sub !)
        elif x>=128>=self.daynight:
            music("night.wav", -1, .7, fade_ms=fade*2)
            sounds.crickets.play(-1, fade_ms=fade*2)
            sounds.wind.play(-1, fade_ms=fade*2)
 
        # Dawn
        elif x<=128<=self.daynight:
            music("music.wav", -1, .7, fade_ms=fade*2)
            sounds.ambiance.play(-1, fade_ms=fade*2)

        # Paused
        if self.paused or self.cutscene:
            pg.mixer.music.pause()

        self.daynight = x

    def draw_floor(self, dt):
        # bg color
        self.display.fill(self.floor_colors[self.player.map])
        # water particles
        if self.player.map == WILD:
            self.water_pcs_idx = (self.water_pcs_idx+ANIM_SPEED*dt) % len(self.water_imgs)
            for f,x,y in self.water_pcs:
                self.display.blit(self.water_imgs[f][int(self.water_pcs_idx)], (x,y) - self.offset)
        # floor
        self.display.blit(self.floors[self.player.map], -self.offset)

    def draw_mask(self):
        mask = self.display.copy()

        # Mines "shader"
        if self.player.map in (MINES,DUNGEON):
            darkness = .4
            mask.fill((255*darkness,255*darkness,255*darkness))

            for prop in self.filtered(self.props):
                if prop.name == 'torch':
                    mask.blit(self.light_mask, self.light_mask.get_rect(center=prop.rect.midbottom + vec2(0,-8*SCALE) - self.offset), special_flags=pg.BLEND_RGB_ADD) 
                elif 'teleport' in PROP_DATA[prop.name] or prop.name == 'campfire':
                    mask.blit(self.light_mask, self.light_mask.get_rect(center=prop.rect.midbottom - self.offset), special_flags=pg.BLEND_RGB_ADD) 
            # Player mask
            mask.blit(self.light_mask, self.light_mask.get_rect(center=(W/2,H/2)), special_flags=pg.BLEND_RGB_ADD) 
            # Queen mask
            if self.queen and self.queen.alive() and self.player.map == DUNGEON:
                mask.blit(self.queen_mask, self.queen_mask.get_rect(center=self.queen.pos - self.offset), special_flags=pg.BLEND_RGB_ADD) 

            mask2 = mask.copy();mask2.fill((255*.2,255*.2,255*.2));mask2.blit(load(self.light_mask, size=self.display.get_size()), (0,0), special_flags=pg.BLEND_RGB_ADD)
            self.display.blit(mask2, (0,0), special_flags=pg.BLEND_RGB_MULT)
            self.display.blit(mask, (0,0), special_flags=pg.BLEND_RGB_MULT)

        elif self.player.map == WILD:
            # Daynight
            self.update_daynight()

            # Torches/campfire
            lightness = .3
            mask.fill('black')
            mask2 = mask.copy();mask2.fill((255*lightness,255*lightness,255*lightness))

            for prop in self.filtered(self.props):
                if prop.name in ('torch','campfire'):
                    mask.blit(self.light_mask, self.light_mask.get_rect(center=prop.rect.midbottom + vec2(0,-8*SCALE) - self.offset), special_flags=pg.BLEND_RGBA_ADD) 
            
            mask.blit(mask2, (0,0), special_flags=pg.BLEND_RGB_MULT)
            self.display.blit(mask, (0,0), special_flags=pg.BLEND_RGB_ADD)
            
    def filtered(self, sprites=None):
        return filter(lambda s: s.pos.distance_to(self.player.pos)<W and s.map == self.player.map, sprites or self.sprites)

    def run(self, dt):
        # Filter
        self.collides_filter = tuple(self.filtered(self.collides))
        self.props_filter = tuple(self.filtered(self.props))
        self.filter = tuple(self.filtered(self.sprites))
        
        # Input
        if not self.cutscene:
            self.input(dt)

        # Timers
        timers_update()
        for timer in self.timers.values():
            timer.update()
        
        # Update
        # sprites (cutscene)
        if self.cutscene:
            for s in self.filter:
                s.animate(dt)
            self.update_cutscene()
        
        # sprites
        elif not self.paused:
            for s in self.filter:
                s.update(dt)
            self.compute_offset()
        particle.update(self)

        # Draw
        if self.game.scene!=self: return
        # - floor
        self.draw_floor(dt)
        particle.draw(self, self.foot_pc)
        particle.draw(self, self.hammer_pc)
        # - sprites
        for sprite in sorted(self.filter, key=lambda s: s.hitbox.bottom):
            pg.draw.rect(self.display, 'green', sprite.rect.move(-self.offset))
            pg.draw.rect(self.display, 'red', sprite.hitbox.move(-self.offset))
            sprite.draw()
        # - particles (no walk_pc)
        particle.draw(self,self.scratch_pc,self.damage_pc,self.bubble_pc)
        # - mask
        self.draw_mask()

        # Overlay
        self.overlay.update()
        self.game.cursor(self.overlay.cursor, self.overlay.display)
        if not self.cutscene:
            self.display.blit(self.overlay.display,(0,0))