from util.support import *
from sprites.entity import Entity
from util.pnj_data import *

PNJ_MM = [2,3,4,5,12]

class PNJ(Entity):
    def __init__(self, data, world, groups):
        self.name = data['name']
        self.world = world
        self.world.pnjs[self.name] = self

        super().__init__(world, data.get('map',WILD), data['pos'], groups, PNJ_HB, "idle", "B")
        
        self.data = pnj_data(self)
        self.options = tuple(k for k in self.data.keys() if '_'not in k)

        self.friend = data.get("friend",0)
        self.quest_idx = data.get("quest",0)
        self.talk_idx = data.get("talk",0)

        self.mm = PNJ_MM[PNJ_IDX.index(self.name)]

        self.house = None
        self.go_home = False
        self.speed *= .3
        self.inside = self.pos.x<0

        self.target = self.pos

    def save(self):
        return {
            "pos": (int(self.pos.x),int(self.pos.y)), 
            "name": self.name,
            "friend": self.friend,
            "quest": self.quest_idx,
            "talk": self.talk_idx,
            "map": self.map,
        }
    
    def load(self, data):
        self.friend, self.quest_idx, self.talk_idx = data

    def load_graphics(self, world):
        ts = self.world.pnj_imgs[self.name]
        
        self.shadows = {}
        animation = {}
        
        def anim(n, y, length, flip=False):
            imgs = ts[y*4:y*4+length]
            if flip: imgs = flips(imgs, 1)

            anims, shadows = [],[]
            for img in imgs:
                shadow, img = get_shadow(img, 4*SCALE)
                shadows.append(shadow); anims.append(img)
            animation[n] = anims
            self.shadows[n] = shadows
        
        anim("idle_B", 0,1)
        anim("idle_T", 1,1)
        anim("idle_R", 2,1)
        anim("idle_L", 2,1, 1)
        anim("move_B", 0,4)
        anim("move_T", 1,4)
        anim("move_R", 2,4)
        anim("move_L", 2,4, 1)
        return animation
    
    def get_side(self):
        if self.direction:
            self.side = ("L","","R")[round(self.direction.x+1)]\
                     or ("T","","B")[round(self.direction.y+1)]
    
    def interact(self):
        if self.talk_idx == 0:
            self.talk()
        else:
            self.world.overlay.open_pnj(self)

    def trade(self, idx):
        i1, a1, i2, a2, _ = self.data['trade'][idx]
 
        if self.world.player.has(i1, a1):
            sounds.click.play()
            self.world.player.removeitem(i1, a1)
            self.world.player.additem(i2, a2)

    def quest(self): 
        # If all quest done
        if self.quest_idx == len(self.data['quest']):
            self.world.overlay.open_dialog([self.name, "I don't need anything for now.", None])
            return
        
        # Get data
        dialog, quest, _thank = self.data['quest'][self.quest_idx]
        
        # Quest callback
        def callback():
            # New quest ?
            if self.name not in self.world.player.quests:
                sounds.quest.play()
                self.world.player.quests.append(self.name)
                self.world.overlay.quest_notif_trans.activate()
                self.world.overlay.quest_notif_trans.pnj = self.name
                
            # Non-item: Verify if done: complete
            if quest[0] in self.world.quests:
                if self.world.quests[quest[0]]:
                    return self.complete_quest()
            # Item quest: verify player has item
            elif self.world.player.has(*quest[0]):
                return [[self.name, f"Give your {quest[0][1]} {ITEMNAMES[quest[0][0]]} ?", {'yes': self.complete_quest, 'no':None}]]

        # Create dialogs list
        dialogs = []
        for text in dialog:
            dialogs.append([self.name, text, None])
        dialogs[-1][2] = callback

        # Open dialog
        self.world.overlay.open_dialog(*dialogs)

    def complete_quest(self):
        """ VERIF DOIT ETRE DEJA FAITE !!! """
        _dialog, quest, thank = self.data['quest'][self.quest_idx]
        
        # give last tool: return
        if quest[0][0] in TOOLS and len(self.world.player.tools) == 1:
            return  [[None, "You should not give your only tool.", None]]
        # restore barn: image
        elif quest[0] == (6,100):
            self.world.barn.image = self.world.props_imgs['abandoned']
            self.world.barn.data = "r"
        # quest done: add friend
        self.quest_idx += 1
        self.friend += 1

        # item transfer
        if quest[0] not in self.world.quests:
            self.world.player.removeitem(*quest[0])
        self.world.player.additem(*quest[1])
        
        # remove from player list
        if self.name in self.world.player.quests:
            self.world.player.quests.remove(self.name)

        # thank dialog
        dialogs = [[self.name, text, None] for text in thank]
        dialogs[-1][2] = self.upfriend
        return dialogs

    def talk(self):
        # If all talk done
        if self.talk_idx == len(self.data['talk']):
            quest_msg = "\n(Take a look at the quests!)" if self.quest_idx<len(self.data['quest']) else ""
            self.world.overlay.open_dialog([None, "You don't know what to talk about."+quest_msg, {
                "Leave": None,
                "Previous dialog": self.data['talk'][self.talk_idx-1],
            }])
            return
        
        self.world.overlay.open_dialog(*self.data['talk'][self.talk_idx])

    def complete_talk(self):
        if self.talk_idx == len(self.data['talk']): return None
        self.talk_idx += 1
        self.friend += 1
        return self.upfriend()
    
    def upfriend(self):
        sounds.friend.play()
        return [
            [None, f"Your friendship rose !\n(new trade unlocked)", None],
            *(self.data["trade"][self.friend-1][-1] or [])
        ]
    
    def repair(self):
        if self.world.player.tools:
            def repair():
                if self.world.player.get_tool() == 14:
                    return [[self.name, "What is this ?", None]]
                elif self.world.player.has(7):
                    if self.world.player.get_tool() == 15:
                        return [[self.name, x, None]for x in ("(scamming you)\nThere is a little hole here...\nWater could leak here...\nLet me fix it...","a moment please...","Done ! hehe.")]
                    self.world.player.removeitem(7)
                    self.world.player.get_tool(1)[1] = TOOL_DURA[self.world.player.get_tool()]
                    return [[self.name, f"Your {TOOLS[self.world.player.get_tool()]} has been repaired.", None]]
                else:
                    return [[self.name, f"No iron, no reparation.\nIt's cost price.", None]]
                
            return [[self.name, f"Do you want me\nto repair your {TOOLS[self.world.player.get_tool()]} ?\nRequire 1 iron.", {
                "Yes": repair,
                "No": None
            }]]
        else:
            return [[self.name, f"You don't have any tool ?!", None]]

    def minerd(self):
        # 1st problem (to win)
        div = randint(2,9)
        mult = randint(1,div-1)
        n = div*randint(2,9)
        # - choices
        r = n//div*mult
        x = randint(0,2)
        if x == 0: a=r+randint(1,10);b=a+randint(1,10)
        elif x==1: a=r-randint(1,10);b=r+randint(1,10)
        else     : a=r-randint(1,10);b=a-randint(1,10)

        # 2nd
        a2 = randint(101,999)
        b2 = randint(101,999)
        r2 = a2*b2
        s = int(r2*randint(-50,50)/100)
        
        choices2 = {
            str(r2): [
                [None, 'What do I see here ?\nA calculator ?', None],
                [None, 'You are not supposed to be able\nto multiply 2-digit numbers.', None],
                [None, 'You CHEATED >;C', None],
            ],
            str(s): [
                [None, "HAHA ! Wrong ! You lost !\nYou suck ! I'm smarter than you >>:-DD", self.complete_talk]
            ]
        }
        items = list(choices2.items()); shuffle(items); choices2 = dict(items)
                        
        # Return dialog
        choices = {
        str(a): [["M1N3RD", "You BRAINDEAD >:[[",None]],
        str(b): [["M1N3RD", "It's a shame talking with you.",None]],
        str(r): [
        ["M1N3RD", "Right !\nJust imagine if you fail at this lmao.", None],
        ["M1N3RD", "N3XT QU3ST10N", None],
        ["M1N3RD", f"I gold is worth {a2} wood prices\nHow many wood is worth {b2} gold ?", choices2],
        ]
        }
        items = list(choices.items()); shuffle(items); choices = dict(items)
        return [
            ["M1N3RD", f"I have {n} chickens and\nI sell {mult}/{div} of them.", None],
            ["M1N3RD", f"How much I have left ?", choices],
        ]


    def update_target(self):
        if not self.target or self.pos.distance_to(self.target) > TS//4: return
        
        # Home
        if self.go_home:
            self.target = None
            self.go_home = False
            self.house.status = "open"
            self.house.frame_idx = 0
            self.house.incoming = self

        # Wander
        elif not self.inside:
            x = choice((0,1))*choice((-1,1))
            y = 0 if x else choice((0,1))*choice((-1,1))
            self.target = self.pos + vec2(x,y) * randint(1,1)*TS

    def enter(self):
        self.inside = True
        self.set_position((-100,100))

    def exit(self, house):
        self.side = "B"
        self.inside = False
        self.set_position(house.rect.midbottom)
    
    def move(self, dt):
        if not self.target: return
        print(self.target-self.pos)
        # Get directions
        vec = self.target - self.pos
        dirs = list(sorted([vec2(1,0),vec2(-1,0),vec2(0,1),vec2(0,-1)], key=lambda d: d.angle_to(vec)))
        print(dirs)
        print()
        for dir in dirs:
            if not self.collision(dir * self.speed * dt): break
        else: return
        self.direction = dir
        self.hitbox.move_ip(dir * self.speed * dt)
        self.set_position()

    def collision(self, dir):
        for s in self.world.collides:
            if s != self and s.hitbox.colliderect(self.hitbox.move(dir)):
                return True
    
    def update(self, dt):
        self.update_target()
        return super().update(dt)