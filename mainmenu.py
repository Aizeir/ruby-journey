from math import sin
from random import choice
import pygame as pg, json

from util.support import *

trans_time = 1000

class Mainmenu:
    def __init__(self, game):
        self.game = game
        self.display = game.display
        self.fade = Timer(2000).activate()
        
        # Fonts
        self.font = font("font.ttf", 20)
        
        # mouse pos
        self.mouse_pos = pg.mouse.get_pos()

        # menus
        self.menu = "title"

        # Floor and logo
        self.logo = load("icon", scale=6)
        self.offset = 0
        self.floor = pg.Surface((W*2, H))
        self.floor.fill(WILDCOLOR)

        SIZE = TS
        self.details = load_tileset('tilesets/details', size=(SIZE,SIZE))
        self.details = self.details[:len(self.details)//2]
        for     y in range(0,self.floor.get_height(),SIZE):
            for x in range(0,self.floor.get_width(),SIZE):
                if not proba(2): continue
                self.floor.blit(self.details[randint(0,len(self.details)-1)],(x,y))
        
        # TITLE SCREEN
        self.title = Timer(2000)
        self.loading = None
        
        def launch_game():
            self.game.scene = self.game.world
            self.game.scene.open()
        @thread
        def callback():
            self.first_time = False
            self.game.new_game(self.loading)
            # New game: begin tale
            if self.loading:
                self.menu = "begin"
                self.begin.activate()
                self.play_music()
            # Continue
            else: launch_game()
            self.loading = None
        self.title_fade = Timer(500, callback)

        self.continue_but = textr("continue", self.font, UI[7],
            center=(W/2,H*.7))
        self.new_but = textr("new game (reset)", self.font, UI[7],
            center=(W/2,H*.8))
        self.button_hover =  [0,0]

        with open("assets/data.json",'r') as file:
            self.first_time = file.read() == ''

        # END SCREEN
        self.end_tale = [textr(text, self.font, UI[6],
            center=(W/2,H*.9+i*128)) for i,text in enumerate([
            "You made it. You got the ruby.",
            "The journey ends here.",
            "",
            "The miner finally joined back the hamlet.",
            "He brought the modest sum of ... 10 gold !",
            "B-But he found his barn turned into carpet :/",
            "",
            "A vote has been organized to know who's the leader.",
            "Unfortunately the miner lost.",
            "Whatever, everyone is now reconciliate",
            "and read to thrive.",
            "",
            "Now that the mines are safe, the hamlet",
            "built its economy with mining",
            "and became prospere again.",
            "",
            "The exploration of the mines revealed",
            "the existence of a ruby deposit.",
            "You are now free to buy more rubies.",
            "",
            "Thanks for playing.",
            "Aizeir",
            ""
        ])]
        self.end_h = self.end_tale[-1][1].bottom-self.end_tale[0][1].y
        self.end = Timer(2*trans_time+len(self.end_tale)*1000, self.end_callback)
        
        # BEGIN SCREEN
        self.begin_tale = [textr(text, self.font, UI[6],
            center=(W/2,H*.9+i*128)) for i,text in enumerate([
            """"§That's it. A ruby.",
            "I need it for my collection of rare items.",
            "According to my sources",
            "someone has one in this hamlet.",
            "We'll see how I'm doing",
            "since I only took one unit of gold...",
            "","""
        ])]
        self.begin_h = self.begin_tale[-1][1].bottom-self.begin_tale[0][1].y
        self.begin = Timer(2*trans_time+1000*len(self.begin_tale), launch_game)

        self.open()
        
    def open(self):
        self.menu = 'title'
        self.title.activate()
        self.play_music()
        self.offset = 0

    def play_music(self):
        #return#!!!
        music("music2.wav", -1, 10, fade_ms=2000)

    def end_callback(self):
        self.game.scene = self.game.world
        self.game.world.play_music()
        self.game.world.timers['end'].activate()

    def event(self, e):
        # 
        if self.menu == "title" and not self.title_fade.active:
            if e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                if self.button_hover[0] and not self.first_time:
                    self.loading = False
                    pg.mixer.music.fadeout(self.title_fade.duration)
                    self.title_fade.activate()
                elif self.button_hover[1-self.first_time]:
                    self.loading = True
                    pg.mixer.music.fadeout(self.title_fade.duration)
                    self.title_fade.activate()

    def draw_title_screen(self):
        trans = self.title.percent()
        fade = 1-self.title_fade.percent()*(self.loading!=None)

        # Logo
        self.logo.set_alpha(fade*255)
        self.display.blit(self.logo, self.logo.get_rect(center=(W/2,H*.6 - trans*H*.25 - (1-fade)*H*.25)))
        
        # Buttons
        for i,but in enumerate((self.continue_but, self.new_but) if not self.first_time else (self.new_but,)):
            # - hover
            self.button_hover[i] = but[1].collidepoint(self.mouse_pos)

            # - draw
            if self.button_hover[i]: but[0].set_alpha(255*fade*trans)
            else: but[0].set_alpha(((sin(pg.time.get_ticks()/500)+1)*70 + 50)*fade*trans)
            self.display.blit(*but)

    def draw_end_screen(self, alpha):
        off = -self.end.percent()*self.end_h
        
        # Logo
        self.logo.set_alpha(alpha)
        self.display.blit(self.logo, self.logo.get_rect(center=(W/2,H*.5+off)))
        
        # Texts
        for t,r in self.end_tale:
            t.set_alpha(alpha)
            self.display.blit(t,r.move(0,off))

    def draw_begin_screen(self, alpha):
        off = -self.begin.percent()*self.begin_h
        
        # Texts
        for t,r in self.begin_tale:
            t.set_alpha(alpha)
            self.display.blit(t,r.move(0,off))

    def draw_transition(self):
        # Get transition timer (and reverse)
        if self.end.active:
            timer = self.end
        elif self.begin.active:
            timer = self.begin
        # No transition: quit
        else: return
        
        # Set alpha
        mask = pg.Surface((W,H))
        alpha = 1
        x = timer.percent()
        if x*timer.duration < trans_time:
            alpha = x*timer.duration/trans_time
        elif (1-x)*timer.duration < trans_time:
            alpha = (1-x)*timer.duration/trans_time

        mask.set_alpha(clamp(0,1-alpha,1)*255)
        self.display.blit(mask,(0,0))
        return alpha*255

    def draw_floor(self):
        self.display.fill('black')
        speed = 4*60*self.dt
        self.offset = (self.offset+speed)%self.floor.get_width()
        if self.offset > self.floor.get_width()-W:
            self.display.blit(self.floor, (-self.offset+self.floor.get_width(),0))
        self.display.blit(self.floor, (-self.offset,0))
        
    def run(self, dt):
        alpha = self.draw_transition()
        self.fade.update()
        self.title.update()
        self.end.update()
        self.begin.update()
        self.title_fade.update()

        self.draw_floor()

        match self.menu:
            case 'title': self.draw_title_screen()
            case 'end': self.draw_end_screen(alpha)
            case 'begin': self.draw_begin_screen(alpha)
        

        self.display.set_alpha(self.fade.percent()*255)
        self.game.cursor([0,2][self.menu in ('end','begin')])
        
