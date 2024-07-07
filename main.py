from mainmenu import Mainmenu
from world import World
from util import *

### BUGS
## BUG PAUSEMENU LAG (trans daynight??)

class Game:
    def __init__(self):
        # Setup
        pg.display.set_caption("Ruby Journey")
        
        self.screen = pg.display.set_mode((W, H), pg.RESIZABLE)
        self.display = self.screen.copy()
        pg.display.set_icon(load("icon"))
        self.clock = pg.time.Clock()

        # Window resize
        self.W,self.H = W,H
        self.fullscreen = False

        # Scenes
        self.world = None
        self.mainmenu = Mainmenu(self)
        self.scene = self.mainmenu

        # Cursors
        pg.mouse.set_visible(0)
        self.cursors = [(img,vec2(32,32)) for img in load_tileset("ui/mouse", size=(64,64), scale=4)]
 
    def new_game(self, reset=False):
        if self.world and not reset: return
        if not reset:
            with open("assets/data.json",'r') as file:
                self.world = World(self, json.load(file))    
        else:
            self.world = World(self, {})    

    def cursor(self, i, display=None):
        press = pg.mouse.get_pressed()[0]
        size = len(self.cursors)//2
        image, off = self.cursors[press*size+i]
        (display or self.display).blit(image, self.scene.mouse_pos-off)

    def loop(self):
        dt = self.clock.tick() / 1000
        self.scene.dt = dt

        for e in pg.event.get():
            if e.type == pg.QUIT:
                #screenshot(self.display, "capture5.png")
                if self.world:
                    with open("assets/data.json","w") as file:
                        json.dump(self.world.save(), file)
                pg.quit()
                sys.exit()

            elif e.type == pg.KEYDOWN and e.key == pg.K_F11:
                self.fullscreen = not self.fullscreen
                self.screen = pg.display.set_mode((W, H), (pg.RESIZABLE|pg.FULLSCREEN if self.fullscreen else pg.RESIZABLE))

            # Screen resize
            elif e.type == pg.VIDEORESIZE:
                self.W,self.H,self.size = *e.size, vec2(e.size)

            # Event scene
            self.scene.event(e)

        # mouse pos
        self.scene.mouse_pos = vec2(pg.mouse.get_pos())
        self.scene.mouse_pos.x *= W/self.W
        self.scene.mouse_pos.y *= H/self.H

        self.scene.run(dt)
        self.screen.blit(pg.transform.scale(self.display, (self.W,self.H)), (0,0))
        pg.display.flip()

g = Game()
while 1:
    g.loop()