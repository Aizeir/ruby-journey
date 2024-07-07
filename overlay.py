import pygame as pg, math
from sprites.pnj import PNJ
from util.pnj_data import PNJ_IDX
from util.support import *


tradex, tradey, trade_space = 77*UI_SCALE, 23*UI_SCALE, UI_SCALE
pnjx, pnjy, pnj_space = 77*UI_SCALE, 21*UI_SCALE, 4*UI_SCALE
quest_space = 5*UI_SCALE
maxtools = 5
mmfloor = {WILD:2,MINES:4,DUNGEON:5}


class Overlay:
    def __init__(self, world):
        self.game = world.game
        self.world = world
        self.player = world.player
        self.display: pg.Surface = pg.Surface((W,H), pg.SRCALPHA, 32)
        self.display.set_colorkey('black')
        self.cursor = 1

        # Font
        self.font = font("font.ttf", 20)
        self.font30 = font("font.ttf", 30)
        self.font10 = font("font.ttf", 10)
        self.font15 = font("font.ttf", 15)

        # Pause menu
        self.pause = textr("Paused", self.font, UI[0],
            center=(W/2,H*.4))
        self.pause_mm = textr("Return to mainmenu", self.font, UI[2],
            center=(W/2,H*.7))
        self.pause_mm_hover = textr("Return to mainmenu", self.font, UI[3],
            center=(W/2,H*.7))
        self.pause_cont = textr("(click to continue)", self.font, UI[1],
            center=(W/2,H*.5))
        
        # Panels
        def panel_None(): self.panel = None
        self.panel_timer = Transition(300, 150, callmid=self.open_panel_dialog, callend=panel_None)
        self.pnj = None
        self.panel = None
        self.dialog_panel = False

        # Trade panel
        self.trade_imgs = load_tileset("ui/trade", (tradex, tradey), UI_SCALE)
        self.trade_rect = rectx((tradex, 4*tradey), "midtop", (W/2,H*.3))

        # PNJ panel
        self.pnj_imgs = load_tileset("ui/pnj", (pnjx, pnjy), UI_SCALE)
        self.pnj_rects = [rectx((pnjx,pnjy),"midtop",(W/2, H*.3+y*(pnjy+pnj_space))) for y in range(4)]
        
        # Dialog
        self.dialog = None
        self.dialog_rect = None
        self.dialog_time = None
        self.dialog_last = None
        self.dialog_choices = {}
        self.faces = load_folder_dict("faces", load, UI_SCALE)
        self.faces_mini = load_folder_dict("faces", load, 3)
        self.dialog_arrows = load_tileset("ui/dialog_arrow", (7*UI_SCALE,8*UI_SCALE), UI_SCALE)

        # Inventory (+items)
        self.items = world.items_imgs
        self.inventory_img = load("ui/inventory", scale=UI_SCALE)
        self.inventory_rect = self.inventory_img.get_rect(bottomleft=(6*UI_SCALE,H-6*UI_SCALE))
        self.inv_idx = 0

        # tip
        tip_img = load("ui/tip", scale=UI_SCALE)
        self.tip_imgs = [tip_img, pg.transform.flip(tip_img, 1,0)]

        # Tools
        self.tab_imgs = load_tileset("ui/tab", (23*UI_SCALE,12*UI_SCALE), UI_SCALE)
        self.tool_limit_img = load("ui/tool_limit", scale=UI_SCALE)
        self.tool_img = load("ui/tool", scale=1)
        self.tool_rects = []
        self.tool_imgs = []
        y = 0
        for h in (20,18,21,24,23):
            self.tool_imgs.append(load(self.tool_img.subsurface(0, y, 20, h), scale=UI_SCALE))
            y += h
        
        # Heart (mines)
        self.heart_imgs = load_tileset("ui/heart", (24*UI_SCALE,21*UI_SCALE), UI_SCALE)

        # Minimap
        self.minimap_img, mask = load_tileset("ui/minimap_ui", (UI_SCALE*48,UI_SCALE*50), UI_SCALE)
        self.minimap_mask = pg.mask.from_surface(mask)
        self.e_imgs = load_tileset("ui/e", (11*UI_SCALE, 13*UI_SCALE), UI_SCALE)
        self.floors = {m:pg.Surface(vec2(surf.get_size())//MMSCALE) for m,surf in self.world.floors.items()}

        self.minimap_floor_ts = load_tileset("ui/minimap_floor", size=(4*UI_SCALE,4*UI_SCALE), scale=UI_SCALE)
        self.minimap_ts = load_tileset("ui/minimap", size=(6*UI_SCALE,6*UI_SCALE), scale=UI_SCALE)

        # Minimap panel
        scale = int(UI_SCALE*2.5)
        self.mmo_img, mask = load_tileset("ui/minimap_ui", (scale*48,scale*50), scale)
        self.mmo_mask = pg.mask.from_surface(mask)
        self.minimap_rect = self.mmo_img.get_rect(center=(W/2,H/2))

        # Quest
        self.quest_icon = load_tileset("ui/quest", (16*UI_SCALE,17*UI_SCALE), UI_SCALE)
        self.quest_rect = self.quest_icon[0].get_rect(topright=(W-6*UI_SCALE,6*UI_SCALE))
        self.quest_notif_trans = Transition(1000, callmid=True)

        self.quest_img = load("ui/questlist", scale=UI_SCALE)
        self.quest_img = [self.quest_img, pg.transform.flip(self.quest_img,1,0)]
        self.quest_face = load("ui/questface", scale=UI_SCALE)
        self.noquest_img = load("ui/noquest", scale=UI_SCALE//2)
        self.quest_heads = load_tileset("ui/heads", (9*UI_SCALE,10*UI_SCALE), UI_SCALE)

        # Interact
        self.interact_imgs = load_tileset("ui/interact", (64*UI_SCALE,20*UI_SCALE), UI_SCALE)

    def busy(self):
        return self.dialog or self.panel

    def input(self, k, m, dt):
        pass

    def event(self, e):
        # Pause
        if not self.busy() and e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
            sounds.pause.play()
            self.world.paused = not self.world.paused
            if self.world.paused:  pg.mixer.music.pause()
            else:                  pg.mixer.music.unpause()
        # Unpause
        if self.world.paused and e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
            sounds.click.play()
            self.world.paused = False
            # Return mainmenu
            if self.pause_mm[1].collidepoint(self.world.mouse_pos):
                self.world.game.scene = self.world.game.mainmenu
                self.world.game.scene.open()
            # Continue
            else:
                pg.mixer.music.unpause()
            return

        # Dialog
        if self.dialog_rect:
            # click - event (sounded)
            if e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                self.event_dialog_click()
            # space - trigger
            elif e.type == pg.KEYDOWN and e.key == pg.K_SPACE:
                sounds.press.play()
                self.dialog_trigger()
        
        # Panel (Trade / PNJ)
        if self.panel_timer.percent() and not (self.dialog_rect and self.dialog_rect.collidepoint(self.world.mouse_pos)):
            # click - event (sounded)
            if e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                if self.panel == "trade": self.event_trade()
                elif self.panel == "pnj": self.event_pnj()
                elif self.panel == "quest": self.event_quest()
                elif self.panel == "mm": self.event_mm()
            
            # escape - quit
            elif e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                sounds.press.play()
                self.close_panel()
                
        # Tools
        if e.type == pg.KEYDOWN and e.key == pg.K_TAB and self.player.tools:
            sounds.press.play()
        elif e.type == pg.KEYUP and e.key == pg.K_TAB and self.player.tools:
            sounds.release.play()
            sounds.switch.play()
            self.player.tool = (self.player.tool+1)%len(self.player.tools)

        # Inventory
        inv_len = len(self.player.inventory.items)
        if e.type == pg.MOUSEWHEEL and inv_len > 5:
            inv_idx = max(0,min(inv_len-5,self.inv_idx-e.y))
            if inv_idx != self.inv_idx:
                sounds.switch.play()
                self.inv_idx = inv_idx

        # Drop blick
        elif e.type == pg.MOUSEBUTTONDOWN and e.button == 1 and self.inventory_rect.collidepoint(self.world.mouse_pos):
            for i, item in enumerate(list(self.player.inventory.items)[self.inv_idx:self.inv_idx+5]):
                pos = self.inventory_rect.topleft+vec2(4*UI_SCALE, 4*UI_SCALE+i*18*UI_SCALE)
                if pg.Rect(pos, (self.items[item].get_size())).collidepoint(self.world.mouse_pos):
                    amount = self.player.inventory.items[item]
                    self.player.inventory.remove(item, amount)
                    self.world.drop_item(item, amount)

        # Quest
        if self.quest_rect.collidepoint(self.world.mouse_pos) and e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
            sounds.click.play()
            if self.panel == "quest":
                sounds.panel.play()
                self.panel_timer.activate(1)
            else:
                self.open_panel("quest")
        # Minimap
        elif e.type == pg.KEYDOWN and e.key == pg.K_e:
            sounds.press.play()
        elif e.type == pg.KEYUP and e.key == pg.K_e:
            sounds.press.play()
            if self.panel == "mm":
                sounds.panel.play()
                self.panel_timer.activate(1)
            else:
                self.close_panel()# explication: qd on ouvre quest on ferme en mm temps pnj (event pnj) or ici c par keypress donc ca ferme pas les panel dialog
                self.open_panel("mm")

    def event_dialog_click(self):
        # On dialog
        if self.dialog_rect.collidepoint(self.world.mouse_pos):
            sounds.click.play()
            self.dialog_trigger()
        # On choice
        elif self.dialog_choices and self.dialog:
            for c, r in self.dialog_choices.items():
                # trigger choice
                if r.collidepoint(self.world.mouse_pos):
                    sounds.click.play()
                    self.dialog_trigger(self.dialog[2][c])
                    break

    def event_trade(self):
        # Sound
        sounds.click.play()

        # Inside - Trade
        if self.trade_rect.collidepoint(self.world.mouse_pos):
            i = (self.world.mouse_pos.y - self.trade_rect.y) // tradey
            if i < self.pnj.friend:
                self.pnj.trade(int(i))
                # sound §?
        # Outside - Quit (+quit dialog)
        else:
            self.close_panel()

    def event_quest(self):
        if self.quest_rect.collidepoint(self.world.mouse_pos): return
        sounds.click.play()
        sounds.panel.play()
        self.panel_timer.activate(1)

    def event_mm(self):
        if self.minimap_rect.collidepoint(self.world.mouse_pos): return
        sounds.click.play()
        sounds.panel.play()
        self.panel_timer.activate(1)

    def event_pnj(self):
        # Sound
        sounds.click.play()
        
        # Quit
        self.close_panel()
        
        # Execute option
        for i, rect in enumerate(self.pnj_rects[:len(self.pnj.options)]):
            if not rect.collidepoint(self.world.mouse_pos):continue
            text = self.pnj.options[i]
            if   text == "quest":
                self.pnj.quest()
            elif text == "trade":
                self.open_panel("trade")
            elif text == "talk":
                self.pnj.talk()
            else:
                # custom function
                if callable(self.pnj.data[text]):
                    self.open_dialog(*self.pnj.data[text]())
                # custom dialog
                else: self.open_dialog(*self.pnj.data[text])

    def open_panel_dialog(self):
        if self.panel not in ('pnj','trade'): return
        # PNJ/Trade dialog
        self.open_dialog(*self.pnj.data['_panel'][self.panel == "trade"])

    def open_panel(self, panel):
        sounds.panel.play()
        self.panel_timer.activate()
        self.panel = panel

    def close_panel(self):
        sounds.panel.play()
        self.panel_timer.activate(1)
        self.dialog = None
        sounds.ptalk.stop()

    def open_pnj(self, pnj):
        self.pnj = pnj
        self.open_panel("pnj")
        
    def open_dialog(self, *dialogs):
        """
        char:str/None, text, trigger:func/None
        """
        if not dialogs: return
        if self.dialog and self.dialog[1] == dialogs[0][1]: 
            self.dialog = None
            return
        
        self.dialog_panel = bool(self.panel and not self.panel_timer.backwards)
        if self.dialog_panel:
            sounds.ptalk.play(-1, fade_ms=1000)
        else:
            sounds.talk.play(-1, fade_ms=100)

        # Set dialog
        self.dialog, dialogs = dialogs[0], list(dialogs[1:])
        
        # Typing
        self.dialog_time = pg.time.get_ticks()
        self.dialog_last = -1

        # Trigger
        # Function: return dialogs
        if callable(self.dialog[2]):
            trigger = self.dialog[2]
            self.dialog[2] = lambda: (trigger() or dialogs)
        # Dict: choices, str: ?
        elif type(self.dialog[2]) not in (dict,str):
            self.dialog[2] = dialogs

    def dialog_trigger(self, trigger=-1):
        if not self.dialog: return
        # Typing
        if (pg.time.get_ticks()-self.dialog_time)//TYPE_TIME < len(self.dialog[1]):
            self.dialog_time = pg.time.get_ticks() - TYPE_TIME * len(self.dialog[1])
            return

        # Trigger (choix...)
        if trigger == -1: trigger = self.dialog[2]
        # Fonction
        if callable(trigger):
            trigger = trigger()

        # List dialogs
        if isinstance(trigger, list) and trigger:
            self.open_dialog(*trigger)
        # Exit dialog
        elif not (trigger or self.dialog_panel):
            self.dialog = None
        # Do nothing
        else: return
        
        # Play sound
        sounds.dclick.play()

    def draw_pause_menu(self):
        self.display.fill(UI[4])
        self.display.blit(*self.pause)
        self.display.blit(*self.pause_cont)
        if self.pause_mm[1].collidepoint(self.world.mouse_pos):
            self.display.blit(*self.pause_mm_hover)
        else:
            self.display.blit(*self.pause_mm)

    def draw_trade(self):
        if self.panel != "trade": return
        
        # Variables
        f = min(4, self.pnj.friend)
        offset_y = H * (1-self.panel_timer.percent())

        # TRADES
        for i, data in enumerate(self.pnj.data['trade']):
            i1,a1,i2,a2, _ = data
            
            # Rect
            y = i*(tradey+trade_space) + offset_y
            rect = pg.Rect(self.trade_rect.x,self.trade_rect.y+y,tradex,tradey)
            
            # image
            hover = rect.collidepoint(self.world.mouse_pos) and i<f
            press = pg.mouse.get_pressed()[0] and hover
            self.display.blit(self.trade_imgs[(i<f)+hover+press], rect)

            # Items
            for item, amount, x in ((i1,a1,15*UI_SCALE),(i2,a2,tradex-15*UI_SCALE)):
                # item
                icon = self.items[item]
                rect = icon.get_rect(center=(
                    self.trade_rect.x+x,
                    self.trade_rect.y+y+tradey/2)
                )
                self.display.blit(icon, rect)

                # amount
                if i<f:
                    ui_outline(self, str(amount), bd=4, font=self.font,
                        midbottom=rect.midbottom)
                
        # Title
        ui_outline(self, self.pnj.name,
            midbottom=self.trade_rect.midtop+vec2(0,offset_y-2*UI_SCALE),
            corner=1, pad=1)
      
    def draw_pnj(self):
        if self.panel != "pnj": return
        
        # Transition
        offset_y = H * (1-self.panel_timer.percent())

        # Options
        for i, rect in enumerate(self.pnj_rects[:len(self.pnj.options)]):
            # rect (transition)
            rect = rect.move(0,offset_y)
        
            # image
            hover = rect.collidepoint(self.world.mouse_pos)
            press = pg.mouse.get_pressed()[0] and hover
            self.display.blit(self.pnj_imgs[hover+press], rect)

            # texts
            text = self.pnj.options[i].upper()
            self.display.blit(*textr(text,self.font,UI[5], center=rect.center+vec2(0,UI_SCALE)))
            self.display.blit(*textr(text,self.font,UI[2], center=rect.center))
    
        # Title
        ui_outline(self, self.pnj.name,
            midbottom=self.pnj_rects[0].move(0,offset_y-2*UI_SCALE).midtop,
            corner=1, pad=1)
        
    def draw_quest(self):
        # Icon
        active = self.panel=='quest' and not self.panel_timer.backwards
        hover = self.quest_rect.collidepoint(self.world.mouse_pos) and not active
        press = pg.mouse.get_pressed()[0] and hover
        self.display.blit(self.quest_icon[hover+press+2*active], self.quest_rect)
        
        # No Quest
        if hover and not self.player.quests:
            self.display.blit(self.noquest_img, self.noquest_img.get_rect(midright=self.quest_rect.midleft+vec2(-2*UI_SCALE, 0)))

        # Quest notif
        self.quest_notif_trans.update()
        x = self.quest_notif_trans.percent(200)
        if x:
            # title, desc, icon
            pnj = self.world.pnjs[self.quest_notif_trans.pnj]
            quest = pnj.data['quest'][pnj.quest_idx][1]
            rect = self.quest_img[0].get_rect(topright=self.quest_rect.topleft+vec2(0,-2*UI_SCALE))
            
            # image
            self.display.blit(self.quest_img[0], rect)
            # text
            self.display.blit(*textr(quest[2],self.font15,UI[7],
                topright=rect.topright+vec2(-10*UI_SCALE,5*UI_SCALE)))
            # desc
            self.display.blit(*textr(quest[3],self.font10,UI[7],
                topright=rect.topright+vec2(-10*UI_SCALE,11*UI_SCALE)))

    def draw_quest_panel(self):
        if self.panel != "quest": return
        
        # Transition
        offset_y = H * (1-self.panel_timer.percent())

        # Quests
        for i, pnj_name in enumerate(self.player.quests):
            # Data + rect
            pnj = self.world.pnjs[pnj_name]
            quest = pnj.data['quest'][pnj.quest_idx][1]
            flip = i%2!=0
            rect = self.quest_img[0].get_rect(midtop=(W/2-(-1)**flip*20*UI_SCALE, H*.35+i*(self.quest_img[0].get_height()+quest_space)+offset_y+2*UI_SCALE))
            
            # image
            self.display.blit(self.quest_img[flip], rect)

            if flip:
                # text
                self.display.blit(*textr(quest[2],self.font15,UI[7],
                    topleft=rect.topleft+vec2(14*UI_SCALE,5*UI_SCALE)))
                # desc
                self.display.blit(*textr(quest[3],self.font10,UI[7],
                    topleft=rect.topleft+vec2(11*UI_SCALE,11*UI_SCALE)))
                # icon
                r = self.quest_face.get_rect(midright=rect.midleft+vec2(-4*UI_SCALE,0))
            else:
                # text
                self.display.blit(*textr(quest[2],self.font15,UI[7],
                    topright=rect.topright+vec2(-14*UI_SCALE,5*UI_SCALE)))
                # desc
                self.display.blit(*textr(quest[3],self.font10,UI[7],
                    topright=rect.topright+vec2(-11*UI_SCALE,11*UI_SCALE)))
                # icon
                r = self.quest_face.get_rect(midleft=rect.midright+vec2(4*UI_SCALE,0))
                
            # icon
            self.display.blit(self.quest_face, r)

            icon = pg.transform.scale2x(self.quest_heads[PNJ_IDX.index(pnj.name)])
            self.display.blit(icon, icon.get_rect(center=r.center))

        # Title
        ui_outline(self, f"Quests ({len(self.player.quests)})",
            midbottom=(W/2, H*.35+offset_y-2*UI_SCALE),
            corner=1, pad=1)

    def draw_dialog(self):
        # Update values
        self.dialog_rect = None
        self.dialog_choices = {}

        # No dialog: quit
        if not self.dialog: return

        # Typing sound
        #  get character idx
        n = min(len(self.dialog[1]), (pg.time.get_ticks()-self.dialog_time)//TYPE_TIME)
        if self.dialog_last != n:
            self.dialog_last = n
        #  stop typing
        dialog_end = n == len(self.dialog[1])
        if dialog_end:
            sounds.talk.stop()
            sounds.ptalk.stop()

        # Variables
        draw_choices = isinstance(self.dialog[2],dict) and dialog_end
        full_text = self.dialog[1][:n]
        if self.dialog_panel:
            full_text = self.dialog[0]+": "+full_text
        
        # Texts list
        texts = []
        for text in full_text.split("\n"):
            texts.append(self.font.render(text, False, UI[6]))
        
        # Background rect
        size = self.font.get_height()
        interline = 8
        margin = 16
        top_margin = margin+8
        bot_margin = margin
        
        w = max(196, *[t.get_width() for t in texts]) + 2*margin
        h = top_margin + len(texts) * (size+interline) - interline + bot_margin
        
        self.dialog_rect = rectx((w,h), "midbottom", (W/2,H-80 + 32*self.dialog_panel))
        if not draw_choices: self.dialog_rect.h += 8
        rect = self.dialog_rect

        # Rect Pad
        pad = 8
        pg.draw.rect(self.display, UI[1], rect)
        pg.draw.rect(self.display, UI[0], (*rect.bottomleft, rect.w, pad))
        
        # Hover (not panel)
        if not self.dialog_panel and not draw_choices and rect.collidepoint(self.world.mouse_pos):
            pg.draw.rect(self.display, UI[2], rect, 6)

        # Texts
        for i, text in enumerate(texts):
            y = rect.y + top_margin + i * (size+interline)
            self.display.blit(text, (rect.x+margin, y))

        # Face Title
        if self.dialog[0] and not self.dialog_panel:
            # face
            name = self.dialog[0].lower() if self.dialog[0] != 'You' else 'player'
            ui_outline(self, self.faces[name], midbottom=rect.midtop)
            # title
            ui_outline(self, self.dialog[0], font=self.font, center=rect.midtop)
        # Face (panel)
        elif self.dialog[0] and dialog_end:
            # pnj
            if self.dialog[0] != 'You':
                name = self.dialog[0].lower()
                ui_outline(self, self.faces_mini[name], font=self.font, bottomleft=rect.topleft+vec2(16,0))
            # player
            else:
                ui_outline(self, self.faces_mini['player'], font=self.font, bottomright=rect.topright+vec2(-16,0))

        # Hover (panel)
        if self.dialog_panel and (self.dialog[2] or not dialog_end) and rect.collidepoint(self.world.mouse_pos):
            pg.draw.rect(self.display, UI[2], rect, 6)

        # Choices
        if draw_choices:
            # constants
            margin = 16
            w = sum([self.font.render(text,0,UI[0]).get_width()+margin for text in self.dialog[2]]) - margin
            x = rect.centerx-w//2
            
            # draw choices
            for i, choice in enumerate(self.dialog[2]):
                # text rect
                t, r = textr(choice, self.font, UI[7],
                    topleft=(x,rect.bottom+16))
                
                # update variables
                self.dialog_choices[choice] = r
                x += r.w + margin

                # hover
                hover = r.collidepoint(self.world.mouse_pos)

                # draw
                pg.draw.rect(self.display,UI[0+hover], r.inflate(6,6).move(0,4))
                pg.draw.rect(self.display,UI[2+hover], r.inflate(6,6))
                self.display.blit(t,r)

        # Arrow
        #  next
        if dialog_end and not isinstance(self.dialog[2],dict) and not self.dialog_panel:
            self.display.blit(self.dialog_arrows[1], self.dialog_arrows[1].get_rect(center=rect.midbottom))
        #  skip
        elif not dialog_end and not self.dialog_panel:
            self.display.blit(self.dialog_arrows[0], self.dialog_arrows[0].get_rect(center=rect.midbottom))

    def draw_inventory(self):
        if not self.player.inventory.items: return

        # Image
        self.display.blit(self.inventory_img, self.inventory_rect)
         
        # Items
        for i, item in enumerate(list(self.player.inventory.items)[self.inv_idx:self.inv_idx+5]):
            pos = self.inventory_rect.topleft+vec2(4*UI_SCALE, 4*UI_SCALE+i*18*UI_SCALE)
            r = pg.Rect(pos, (self.items[item].get_size()))
            hover = r.collidepoint(self.world.mouse_pos)

            # item
            if hover:
                ui_outline(self, self.items[item], corner=True, color=UI[6], topleft=pos)
            else:
                self.display.blit(self.items[item], pos)
                
            # amount
            """ui_outline(self, str(self.player.inventory.items[item]), font=self.font,
                topleft=pos+vec2(7*UI_SCALE, 6*UI_SCALE))"""
            self.display.blit(*textr(str(self.player.inventory.items[item]), self.font, UI[7],
                topleft=pos+vec2(7*UI_SCALE, 6*UI_SCALE)))
            
            # tip
            if hover:
                r.right = self.inventory_rect.right
                self.draw_tip(r, item)

    def draw_tip(self, slot, item, tool=False):
        # Rect
        if tool:
            rect = self.tip_imgs[0].get_rect(midright=slot.midleft+vec2(-2*UI_SCALE,0))
        else:
            rect = self.tip_imgs[0].get_rect(midleft=slot.midright+vec2(2*UI_SCALE,0))
        self.display.blit(self.tip_imgs[not tool], rect)

        # Item
        self.display.blit(*textr(f"{ITEMNAMES[item]}", self.font15, UI[7],
            topleft=rect.topleft+vec2(10,4)*UI_SCALE))

        # Tip
        self.display.blit(*textr(ITEMS[ITEMNAMES[item]].split("\n")[0], self.font10, UI[7],
            topleft=rect.topleft+vec2(10,11.5)*UI_SCALE))

    def draw_tools(self):
        plr = self.player
        if not plr.tools: return

        # Variables
        length = min(len(self.player.tools),maxtools)
        
        # Draw tools
        tip = None
        self.tool_rects.clear()
        for i in range(length):
            # tool data
            tool, data = plr.tools[(plr.tool+i)%len(self.player.tools)]
            durastr = str(math.ceil(data*100/TOOL_DURA[tool]) if data!=-1 else -1)+"%"
    
            # image
            if i==0:         img = self.tool_imgs[3]
            elif length==2:  img = self.tool_imgs[4]
            elif i==1:       img = self.tool_imgs[2]
            elif i!=length-1:img = self.tool_imgs[1]
            else:            img = self.tool_imgs[0]

            # rect
            bottom = H-(6 + (i>0)*(24+2) + (i>1)*21 + max(0,i-2)*18)*UI_SCALE
            rect = img.get_rect(bottomright=(W-6*UI_SCALE,bottom))
            self.tool_rects.append(rect)
            hover = rect.collidepoint(self.world.mouse_pos)

            # tip
            if hover: tip = (rect, tool)

            # draw
            self.display.blit(img, rect)
            
            # dura
            if not hover and TOOL_DURA[tool] != -1: self.display.blit(*textr(durastr, self.font, UI[7],
                midright=rect.midleft+vec2(-4,0)))

            # tool image
            image = self.items[tool]
            r = image.get_rect(center=rect.center)
            # outline
            if hover: ui_outline(self, image, corner=True, color=UI[7], topleft=r.topleft)
            # draw
            else: self.display.blit(image, r)

        # Tool limit
        if len(self.player.tools) > maxtools:
            # image
            r = self.tool_limit_img.get_rect(midbottom=rect.midtop+vec2(0,-1*UI_SCALE))
            self.display.blit(self.tool_limit_img, r)
            # amount
            self.display.blit(*textr(str(len(self.player.tools) - maxtools), self.font, UI[7],
                topleft=r.topleft+vec2(9*UI_SCALE,2*UI_SCALE+1)))

        # TAB
        rect = self.tool_rects[0]
        r = self.tab_imgs[0].get_rect(midright=(rect.x-2*UI_SCALE, rect.y-1*UI_SCALE))
        self.display.blit(self.tab_imgs[2*pg.key.get_pressed()[pg.K_TAB]], r)

        # Tip
        if tip:
            self.draw_tip(*tip, True)

    def draw_interact(self):
        if not (self.player.timers['interact'].active or self.player.interact): return

        # Rect
        rect = self.interact_imgs[0].get_rect(midbottom=(W/2, H+64-112*self.player.timers['interact'].percent()))
        hover = rect.collidepoint(self.world.mouse_pos)
        press = pg.key.get_pressed()[pg.K_SPACE] and not hover
        self.display.blit(self.interact_imgs[hover+press*2], rect)

        # Text
        if self.player.interact:
            self.interact_text = self.font.render(self.player.interact.name, False, UI[2])
        self.display.blit(self.interact_text, self.interact_text.get_rect(midtop=rect.midtop+vec2(2,(9+press*2)*UI_SCALE)))

    def draw_health(self):
        #if self.player.map not in (MINES,DUNGEON): return §
        heart = self.heart_imgs[min(self.player.health, len(self.heart_imgs)-1)]
        self.display.blit(heart, heart.get_rect(midtop=(66*UI_SCALE,20*UI_SCALE)))

    def draw_minimap(self):
        # Setup minimap surf
        size = self.minimap_img.get_width()
        mm = pg.Surface((size,size))
        mm.fill(self.minimap_floor_ts[mmfloor[self.player.map]].get_at((0,0)))
        
        # Floor
        offset = vec2(self.player.rect.center)//MMSCALE-vec2(size,size)/2
        mm.blit(self.floors[self.player.map], -offset)

        # Sprites
        for s in self.world.mms:
            if s.map != self.player.map: continue
            mm.blit(self.minimap_ts[s.mm], self.minimap_ts[s.mm].get_rect(center=s.pos//MMSCALE-offset))
        
        # Drawing to display
        pos = (4*UI_SCALE, 4*UI_SCALE)
        rect = self.minimap_img.get_rect(topleft=pos)
        self.display.blit(self.minimap_mask.to_surface(pg.Surface((size,size)), setsurface=mm,unsetcolor=(0,0,0,0)), pos)
        self.display.blit(self.minimap_img, rect)

        # Open button
        r = self.e_imgs[0].get_rect(center=rect.midbottom+vec2(2*UI_SCALE, 0))
        self.display.blit(self.e_imgs[2*pg.key.get_pressed()[pg.K_e]], r)
    
    def draw_mm_panel(self):
        if self.panel != "mm": return

        # Transition
        offset_y = H * (1-self.panel_timer.percent())

        # Setup minimap surf
        size = self.mmo_img.get_width()
        mm = pg.Surface((size,size))
        mm.fill(self.minimap_floor_ts[mmfloor[self.player.map]].get_at((0,0)))
        
        # Floor
        offset = vec2(self.player.rect.center)//MMSCALE-vec2(size,size)/2
        floor = self.floors[self.player.map]
        mm.blit(floor, -offset)

        # Sprites
        for s in self.world.mms:
            if s.map != self.player.map: continue
            if isinstance(s, PNJ) and s.inside: continue
            mm.blit(self.minimap_ts[s.mm], self.minimap_ts[s.mm].get_rect(center=s.pos//MMSCALE-offset))
        
        # Drawing to display
        self.display.blit(self.mmo_mask.to_surface(pg.Surface((size,size)), setsurface=mm,unsetcolor=(0,0,0,0)), self.minimap_rect.topleft+vec2(0,offset_y))
        self.display.blit(self.mmo_img, self.minimap_rect.move(0, offset_y))

    def draw_transitions(self):
        x=     self.player.timers['dead'].percent()
        x=x or self.world.timers['map'].percent()
        x=x or self.world.timers['begin'].percent()
        x=x or self.world.timers['end'].percent()
        if not x: self.display.set_alpha(255); return
        
        mask = pg.Surface((W,H))
        self.display.set_alpha(max(0,1-4*x)*255)
        mask.set_alpha(x*255)
        self.world.display.blit(mask, (0,0))

    def get_cursor(self):
        pos = self.world.mouse_pos
        if self.world.paused:
            return 0
        if self.panel == "trade" and self.trade_rect.collidepoint(pos):
            return 0
        if self.panel == "pnj" and any([r.collidepoint(pos) for r in self.pnj_rects[:len(self.pnj.options)]]):
            return 0
        if self.panel == "mm" and self.minimap_rect.collidepoint(pos):
            return 0
        if self.quest_rect.collidepoint(pos):
            return 0
        if self.inventory_rect.collidepoint(pos):
            return 0
        if any([r.collidepoint(pos) for r in self.tool_rects[:min(maxtools, len(self.player.tools))]]):
            return 0
        if self.dialog_rect and self.dialog_rect.collidepoint(pos):
            return 0
        if self.dialog and self.dialog_choices and any([r.collidepoint(pos) for r in self.dialog_choices.values()]):
            return 0
        return 1

    def update(self):
        self.display.fill((0,0,0,0))

        if self.world.paused:
            self.draw_pause_menu()
            return
        elif self.player.status == 'dead':
            self.draw_health()
            self.draw_transitions()
            return
        self.panel_timer.update()
        self.cursor = self.get_cursor()
        
        # fixed
        self.draw_minimap()
        self.draw_inventory()
        self.draw_tools()
        # below panels
        self.draw_health()
        self.draw_interact()
        # panels
        self.draw_pnj()
        self.draw_trade()
        self.draw_quest_panel()
        self.draw_mm_panel()
        # above panels
        self.draw_quest()
        self.draw_dialog()
        # black mask
        self.draw_transitions()
