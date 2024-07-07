import pygame as pg, math
from util import *


panelx, panely = 75*UI_SCALE, 18*UI_SCALE
panel_space = 8
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
        self.fontbig = font("font.ttf", 30)
        self.fontsmall = font("font.ttf", 10)
        self.fontshort = font("font.ttf", 15)

        # Pause menu
        self.pause = textr("Paused", self.font, UI[0],
            center=(W/2,H*.4))
        self.pause_mm = textr("Return to mainmenu", self.font, UI[2],
            center=(W/2,H*.7))
        self.pause_mm_hover = textr("Return to mainmenu", self.font, UI[3],
            center=(W/2,H*.7))
        self.pause_cont = textr("(click to continue)", self.font, UI[1],
            center=(W/2,H*.5))
        
        # Key pressed
        self.press = None
        
        # Panels
        def panel_None(): self.panel = None
        self.panel_timer = Transition(300, 150, callmid=self.open_panel_dialog, callend=panel_None)
        self.noquest_timer = Timer(1000)
        self.pnj = None
        self.panel = None
        self.dialog_panel = False

        # Trade panel
        self.trade_imgs = load_tileset("ui/trade", (panelx, panely), UI_SCALE)
        self.trade_rect = pg.Rect(0,0, panelx,4*panely).move_to(midtop=(W/2,H*.35))

        # PNJ panel
        self.pnj_imgs = load_tileset("ui/pnj", (panelx, panely), UI_SCALE)
        self.pnj_rects = [pg.Rect(0,0, panelx,panely).move_to(midtop=(W/2, H*.35+y*(panely+panel_space))) for y in range(4)]
        
        # Dialog
        self.dialog = None
        self.dialog_rect = None
        self.dialog_time = None
        self.dialog_last = None
        self.dialog_choices = {}
        self.faces = load_folder_dict("faces", 4)
        self.faces_mini = load_folder_dict("faces", 3)

        # arrows
        arrow, arrow2 = load_tileset("ui/arrow", (10*4,7*4), 4)
        self.arrow =  [pg.transform.rotate(arrow,90),pg.transform.rotate(arrow,-90), arrow, pg.transform.flip(arrow,0,1)]
        self.arrow2 = [pg.transform.rotate(arrow2,90),pg.transform.rotate(arrow2,-90), arrow2, pg.transform.flip(arrow2,0,1)]

        # Inventory (+items)
        self.items = load_tileset("tilesets/items", (64,64), 4)
        self.inventory_img = load("ui/inventory", UI_SCALE)
        self.inventory_rect = self.inventory_img.get_rect(bottomleft=(32,H-64))
        self.inv_idx = 0

        # tip
        self.tip_img = load("ui/tip", UI_SCALE)

        # Tools
        self.tools_imgs = load_tileset("ui/tool", (20*UI_SCALE,20*UI_SCALE), UI_SCALE)
        self.tab_imgs = load_tileset("ui/tab", (21*UI_SCALE,12*UI_SCALE), UI_SCALE)
        self.tool_limit_img = load("ui/tool_limit", UI_SCALE)
        self.tool_rects = [pg.Rect(0,0, *self.tools_imgs[0].get_size()).move_to(bottomright=vec2(W-48, H-80-(self.tools_imgs[0].get_height()+UI_SCALE)*y)) for y in range(maxtools)]
        
        # Heart (mines)
        self.heart_imgs = load_tileset("ui/heart", (13*SCALE*2,11*SCALE*2), SCALE*2)

        # Minimap
        self.minimap_img, mask = load_tileset("ui/minimap", (UI_SCALE*48,UI_SCALE*48), UI_SCALE)
        self.minimap_mask = pg.mask.from_surface(mask)
        self.minimap_open_img = load_tileset("ui/mmopen", (11*UI_SCALE, 12*UI_SCALE), UI_SCALE)

        scale = int(UI_SCALE*2.5)
        self.mmo_img, mask = load_tileset("ui/minimap", (scale*48,scale*48), scale)
        self.mmo_mask = pg.mask.from_surface(mask)
        self.minimap_rect = self.mmo_img.get_rect(center=(W/2,H/2))

        # Quest
        self.quest_icon = load_tileset("ui/quest", (64,64), 4)
        self.quest_rect = self.quest_icon[0].get_rect(topright=(W-48,32))
        self.quest_notif_timer = Timer(1000)

        self.quest_img = load("ui/questlist", UI_SCALE)
        self.quest_rects = [pg.Rect(0,0, *self.quest_img.get_size()).move_to(midtop=(W/2, H*.35+y*(self.quest_img.get_height()+panel_space))) for y in range(len(self.world.pnjs))]
        self.noquest_img = load("ui/noquest", UI_SCALE//2)

        # Interact
        self.interact_imgs = load_tileset("ui/interact", (64*UI_SCALE,18*UI_SCALE), UI_SCALE)

    def busy(self):
        return self.dialog or self.panel

    def input(self, k, m, dt):
        pass

    def event(self, e):
        # Pause key (pause/unpause)
        if not self.busy() and e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
            sounds.pause.play()
            self.world.paused = not self.world.paused
            (pg.mixer.music.unpause, pg.mixer.music.pause)[self.world.paused]()

        # Pause menu events (return or continue)
        if self.world.paused:
            if e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
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
            if e.type == pg.KEYDOWN and e.key == pg.K_SPACE:
                sounds.press.play()
                self.dialog_trigger()
    
        # Interact
        if self.player.interact:
            if e.type == pg.KEYDOWN and e.key == pg.K_SPACE:
                sounds.press.play()
                self.press = "interact"
            elif e.type == pg.KEYUP and e.key == pg.K_SPACE and self.press == "interact":
                sounds.release.play()
                self.press = None
                self.player.interact.interact()
        
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
        if self.player.tools:
            if e.type == pg.KEYDOWN and e.key == pg.K_TAB:
                sounds.press.play()
                self.press = "tools"
            elif e.type == pg.KEYUP and e.key == pg.K_TAB and self.press == "tools":
                sounds.release.play()
                self.press = None
            
                sounds.switch.play()
                self.player.tool = (self.player.tool+1)%len(self.player.tools)

        # Inventory
        inv_len = len(self.player.inventory.items)
        if inv_len > 5 and e.type == pg.MOUSEWHEEL:
            inv_idx = max(0,min(inv_len-5,self.inv_idx-e.y))
            if inv_idx != self.inv_idx:
                sounds.switch.play()
                self.inv_idx = inv_idx

        # Quest
        if self.quest_rect.collidepoint(self.world.mouse_pos):
            if e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                sounds.click.play()
                if self.panel == "quest":
                    sounds.panel.play()
                    self.panel_timer.activate(1)
                elif not self.player.quests:
                    self.quest_notif_timer.toggle()
                else:
                    self.open_panel("quest")

        # Minimap
        if e.type == pg.KEYDOWN and e.key == pg.K_e:
            sounds.press.play()
            self.press = "minimap"
        elif e.type == pg.KEYUP and e.key == pg.K_e and self.press == "minimap":
            sounds.press.play()
            self.press = None

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
            i = (self.world.mouse_pos.y - self.trade_rect.y) // panely
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
            y = i*panely + offset_y
            rect = pg.Rect(self.trade_rect.x,self.trade_rect.y+y,panelx,panely)
            
            idx = i*3 + (i<f) + (i<f and self.player.inventory.has(i1,a1) and rect.collidepoint(self.world.mouse_pos))
            self.display.blit(self.trade_imgs[idx], rect)

            # Indications
            self.display.blit(*textr(("-",">")[i<f], self.font, UI[0],
                center=(self.trade_rect.x+panelx/2,self.trade_rect.y+y+panely/2)))
            
            # Items
            for item, amount, x in ((i1,a1,1),(i2,a2,3)):
                # item
                icon = self.items[item]
                rect = icon.get_rect(center=(
                    self.trade_rect.x+panelx*x/4,
                    self.trade_rect.y+y+panely/2)
                )
                self.display.blit(icon, rect)

                # amount
                if i<f: self.display.blit(*textr(str(amount),self.font,UI[0],
                    midbottom=rect.midbottom))
                
        # Title
        ui_outline(self, self.pnj.name,
            midbottom=self.trade_rect.midtop+vec2(0,offset_y))
      
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
            idx = ((i!=0) + (i==len(self.pnj.options)-1))*2+hover
            self.display.blit(self.pnj_imgs[idx], rect)

            # texts
            text = self.pnj.options[i].upper()
            self.display.blit(*textr(text,self.font,UI[5], center=rect.center+vec2(0,UI_SCALE)))
            self.display.blit(*textr(text,self.font,UI[2], center=rect.center))
    
        # Title
        ui_outline(self, self.pnj.name,
            midbottom=self.pnj_rects[0].move(0,offset_y).midtop)
        
    def draw_quest(self):
        # Icon
        active = self.panel=='quest' and not self.panel_timer.backwards
        hover = self.quest_rect.collidepoint(self.world.mouse_pos) and not active
        self.display.blit(self.quest_icon[active+2*hover], self.quest_rect)
        
        # Notifs
        self.quest_notif_timer.update()
        x = self.quest_notif_timer.percent(0)
        
        # No Quest
        if x and not self.player.quests:
            self.display.blit(self.noquest_img, self.noquest_img.get_rect(midright=self.quest_rect.midleft+vec2(-UI_SCALE, 0)))
        # Quest notif
        elif x:
            # title, desc, icon
            pnj = self.world.pnjs[self.quest_notif_timer.pnj]
            rect = self.quest_img.get_rect(topright=self.quest_rect.topleft+vec2(0,-UI_SCALE))
            self.draw_quest_img(rect, pnj)

    def draw_quest_panel(self):
        if self.panel != "quest": return
        
        # Transition
        offset_y = H * (1-self.panel_timer.percent())

        # Quests
        for i, rect in enumerate(self.quest_rects[:len(self.player.quests)]):
            self.draw_quest_img(
                rect.move(0,offset_y),
                self.world.pnjs[self.player.quests[i]]
            )
    
        # Title
        ui_outline(self, f"Quests ({len(self.player.quests)})", 
            midbottom=self.quest_rects[0].move(0,offset_y).midtop)

    def draw_quest_img(self, rect, pnj):
        # image
        self.display.blit(self.quest_img, rect)

        # text
        quest = pnj.data['quest'][pnj.quest_idx][1]
        self.display.blit(*textr(quest[2],self.font,UI[7],
            topleft=rect.topleft+vec2(20*UI_SCALE,4*UI_SCALE-2)))
        
        # desc
        self.display.blit(*textr(quest[3],self.fontsmall,UI[7],
            topleft=rect.topleft+vec2(20*UI_SCALE,11*UI_SCALE-2)))
        
        # icon
        icon = load(self.world.mm2[pnj.mm], 3)
        self.display.blit(icon, icon.get_rect(
            topleft=rect.topleft+vec2(-UI_SCALE-2,2*UI_SCALE)))

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
        
        self.dialog_rect = pg.Rect(0,0, w,h).move_to(midbottom=(W/2,H-80 + 32*self.dialog_panel))
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
            ui_outline(self, self.dialog[0], big=False, center=rect.midtop)
        # Face (panel)
        elif self.dialog[0] and dialog_end:
            # pnj
            if self.dialog[0] != 'You':
                name = self.dialog[0].lower()
                ui_outline(self, self.faces_mini[name], big=False, bottomleft=rect.topleft+vec2(16,0))
            # player
            else:
                ui_outline(self, self.faces_mini['player'], big=False, bottomright=rect.topright+vec2(-16,0))

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
            self.display.blit(self.arrow2[1], self.arrow2[1].get_rect(center=rect.midbottom))
        #  skip
        elif not dialog_end and not self.dialog_panel:
            self.display.blit(self.arrow2[3], self.arrow2[3].get_rect(center=rect.midbottom))

    def draw_inventory(self):
        if not self.player.inventory.items: return
        margin = 8
        size = 64+2*margin

        # Image
        self.display.blit(self.inventory_img, self.inventory_rect)
         
        # Items
        for i, item in enumerate(list(self.player.inventory.items)[self.inv_idx:self.inv_idx+5]):
            pos = self.inventory_rect.topleft+vec2(margin, i*size+margin)
            r = pg.Rect(pos, (self.items[item].get_size()))
            hover = r.collidepoint(self.world.mouse_pos)

            # item
            if hover:
                ui_outline(self, self.items[item], corner=True, color=UI[6], topleft=pos)
            else:
                self.display.blit(self.items[item], pos)
                
            # amount
            self.display.blit(*textr(str(self.player.inventory.items[item]), self.font, UI[7],
                center=pos+vec2(size/2, size/2)))
            
            # tip §
            if hover:
                self.draw_tip(r, item, self.player.inventory.items[item])

        # Arrows
        if len(self.player.inventory.items) > 5:
            off = vec2(0,math.sin(pg.time.get_ticks()/100)*4)
            # up
            if self.inv_idx != 0:
                self.display.blit(self.arrow[2], self.arrow[2].get_rect(center=self.inventory_rect.midtop+off))
            # down
            if self.inv_idx != len(self.player.inventory.items) - 5:
                self.display.blit(self.arrow[3], self.arrow[3].get_rect(center=self.inventory_rect.midbottom+off))

    def draw_tip(self, slot, item, x, tool=False):
        # Rect
        if tool:
            rect = self.tip_img.get_rect(midright=slot.midleft+vec2(-2*UI_SCALE,0))
        else:
            rect = self.tip_img.get_rect(midleft=slot.midright+vec2(4*UI_SCALE,0))
        self.display.blit(self.tip_img, rect)

        # Item
        self.display.blit(*textr(f"{ITEMNAMES[item]}", self.font, UI[7],
            topleft=rect.topleft+vec2(9,3)*UI_SCALE))
        
        # Amount
        if not (tool and "-" in x):
            self.display.blit(*textr(f"[{x}]", self.font, UI[7],
                topright=rect.topright+vec2(-3,3)*UI_SCALE))

        # Tip
        for i, line in enumerate(ITEMS[ITEMNAMES[item]].split("\n")):
            self.display.blit(*textr(line, self.fontsmall, UI[7],
                midtop=rect.midtop+vec2(0,12*UI_SCALE + 20*i)))

    def draw_tools(self):
        plr = self.player
        if not plr.tools: return

        # Variables
        length = min(len(self.player.tools),maxtools)
        
        # Draw tools
        for i in range(length):
            # tool data
            tool, data = plr.tools[(plr.tool+i)%len(self.player.tools)]
            durastr = str(math.ceil(data*100/TOOL_DURA[tool]) if data!=-1 else -1)+"%"
            
            # rect
            rect = self.tool_rects[i]
    
            # image
            hover = rect.collidepoint(self.world.mouse_pos)
            img = self.tools_imgs[(i!=0)]
            self.display.blit(img, rect)

            # tip
            if hover: self.draw_tip(rect, tool, durastr, True)
            
            # dura
            elif TOOL_DURA[tool] != -1: self.display.blit(*textr(durastr, self.font, UI[7],
                midright=rect.midleft+vec2(-4,0)))

            # image
            image = self.items[tool]
            r = image.get_rect(center=rect.center)
            # item
            if hover:
                ui_outline(self, image, corner=True, color=UI[7], topleft=r.topleft)
            else:
                self.display.blit(image, r)

        # Tool limit
        if len(self.player.tools) > maxtools:
            # image
            r = self.tool_limit_img.get_rect(midbottom=rect.midtop+vec2(0,-1*UI_SCALE))
            self.display.blit(self.tool_limit_img, r)
            # amount
            self.display.blit(*textr(str(len(self.player.tools) - maxtools), self.font, UI[7],
                topleft=r.topleft+vec2(9*UI_SCALE,2*UI_SCALE+1)))

        # TAB
        r = self.tab_imgs[0].get_rect(midtop=(rect.centerx, self.tool_rects[0].bottom+1*UI_SCALE))
        self.display.blit(self.tab_imgs[self.press=="tools"], r)

    def draw_interact(self):
        if not (self.player.timers['interact'].active or self.player.interact): return

        # Rect
        rect = self.interact_imgs[0].get_rect(midbottom=(W/2, H+64-112*self.player.timers['interact'].percent()))
        self.display.blit(self.interact_imgs[self.press=="interact"], rect)

        # Text
        if self.player.interact:
            self.interact_text = self.font.render(self.player.interact.name, False, UI[7])
        self.display.blit(self.interact_text, self.interact_text.get_rect(midtop=rect.midtop+vec2(2,(8+(self.press=="interact"))*UI_SCALE+1)))

    def draw_health(self):
        if self.player.map not in (MINES,DUNGEON): return
        heart = self.heart_imgs[4]#self.heart_imgs[self.player.health]
        self.display.blit(heart, heart.get_rect(midtop=(W/2,H*.1)))

    def draw_minimap(self):
        # Setup minimap surf
        size = self.minimap_img.get_width()
        mm = pg.Surface((size,size))
        mm.fill(self.world.mm[mmfloor[self.player.map]].get_at((0,0)))
        
        # Floor
        offset = vec2(self.player.rect.center)//MMSCALE-vec2(size,size)/2
        floor = self.world.floors_mm[self.player.map]
        mm.blit(floor, -offset)

        # Sprites
        for s in self.world.mms:
            if s.map != self.player.map: continue
            mm.blit(self.world.mm2[s.mm], self.world.mm2[s.mm].get_rect(center=s.pos//MMSCALE-offset))
        
        # Drawing to display
        pos = (24, 24)
        rect = self.minimap_img.get_rect(topleft=pos)
        self.display.blit(self.minimap_mask.to_surface(pg.Surface((size,size)), setsurface=mm,unsetcolor=(0,0,0,0)), pos)
        self.display.blit(self.minimap_img, rect)

        # Open button
        r = self.minimap_open_img[0].get_rect(center=rect.midbottom+vec2(2*UI_SCALE, 0))
        self.display.blit(self.minimap_open_img[self.press=="minimap"], r)
    
    def draw_mm_panel(self):
        if self.panel != "mm": return

        # Transition
        offset_y = H * (1-self.panel_timer.percent())

        # Setup minimap surf
        size = self.mmo_img.get_width()
        mm = pg.Surface((size,size))
        mm.fill(self.world.mm[mmfloor[self.player.map]].get_at((0,0)))
        
        # Floor
        offset = vec2(self.player.rect.center)//MMSCALE-vec2(size,size)/2
        floor = self.world.floors_mm[self.player.map]
        mm.blit(floor, -offset)

        # Sprites
        for s in self.world.mms:
            if s.map != self.player.map: continue
            mm.blit(self.world.mm2[s.mm], self.world.mm2[s.mm].get_rect(center=s.pos//MMSCALE-offset))
        
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
        if self.panel == "quest" and any([r.collidepoint(pos) for r in self.quest_rects[:len(self.world.pnjs)]]):
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
        elif self.player.dead:
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
