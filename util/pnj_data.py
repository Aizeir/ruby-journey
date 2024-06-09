from util import *


PNJ_IDX = ('explorer','blacksmith','fisherman','miner','lumberjack')

def pnj_data(pnj): return {
"explorer" : {
    "_panel": [
        [
            ["Explorer", "Hello what's up ?", None],
            ["You", "I'm fine.", None],
            ["Explorer", "You still think of that ruby ?", None],
            ["You", "Yes. Else I wouldn't stay in that slum.", None],
            ["Explorer", "I don't think you can gather 6 gold.", None],
            ["You", "You'll see. I will gather them.", None],
            ["You", "Anyways I'll find a way to get the ruby.", None],
            ["Explorer", "Very good determination kid.", None],
            ["Explorer", "- But how you suck at fight !", None],
            ["You", "Shut up.", None],
        ],
        [
            ["Explorer", "What would you like ?", None],
            ["You", "I don't know...", None],
            ["Explorer", "Take your time.", None],
            ["Explorer", "It's a calm game after all.", None],
        ]
    ],
    "talk": [
        [
            ["You", "Hello. I'm just passing by.", None],
            ["Explorer", "Hello !\nI'm the explorer.\nNice to meet you !", None],
            ["You", "I heard you have a ruby.", None],
            ["Explorer", "Yes a-and ?", None],
            ["You", "Can I get it for free ?", None],
            ["Explorer", "Yes of course !\n...\nMY D*CK YOU GET IT FOR FREE", None],
            ["You", "aNd what IF I tAKe IT BY fORCe ?", None],
            [None, "You fought with him\nand lost the fight.", None],
            ["You", "I'm sorry I'm losing my mind.", None],
            ["Explorer", "Uhm.. But still you can\nbuy it with gold.", None],
            ["You", "How much gold ? I have 1.", None],
            ["Explorer", "Dude it's 6 gold and we can't negociate.\nPlus I'm not ready to leave a such item\nto an untrusthy person.", None],
            ["You", "Alright. Thank you !", pnj.complete_talk],
        ],
        [
            [None, "Talk to the explorer.", {
                "Yes": [
                    ['Explorer', "Before, we had a chicken coop.\nWe sell chicken to the butcherys.", None],
                    ['Explorer', "That's how we were living.\nIt was a prospere activity...", None],
                    ['Explorer', "We were 6. It was our apogee.\nWe were about to sign\na contract with a brand...", None],
                    ['Explorer', "...", {
                    "Continue": [
                    ['Explorer', "But, after a stormy night,\nwe found our barn ravaged.\nAnd all chicken escaped.", None],
                    ['Explorer', "We had to give up this activity.\n2 of us left the hamlet.\nIncluding our former leader the farmer.", None],
                    ['Explorer', "...", {
                    "Continue": [
                    ['Explorer', "But the rest of us stayed here.\nI became the new chief of our group.", None],
                    ['Explorer', "We decided to open a mine\nand live from it.", None],
                    ['Explorer', "But we found it full of wild beasts.\nWe temporarily closed it.", None],
                    ['Explorer', "...", {
                    "Continue": [
                    ['Explorer', "Then, one of us had an idea.\nWe had a lake and\ncan live from fishing !", None],
                    ['Explorer', "That's why our former merchant\nis now the fisherman.", None],
                    ['Explorer', "It doesn't make us very rich,\nbut it's enough for now.\nI'm optimistic now.", None],
                    ['Explorer', "And that's when you come, fellow guest,\nYou can even join us and\nbe the chicken hunter !", None],
                    ['Explorer', "...", pnj.complete_talk],
                    ],
                    "Leave": [['You', "I have to go.", None]],
                    }],
                    ],
                    "Leave": [['You', "I have to go.", None]],
                    }],
                    ],
                    "Leave": [['You', "I have to go.", None]],
                    }],
                    
                ],
                "No": None
            }],
        ],
    ],
    "trade": [
        # I1,A1, I2,A2, dialog
        (0,1, 17,1, [
            ["Explorer", "With 1 gold...", None],
            ["Explorat", "I can exchange your gold for 1 bronze !", None],
            ["You", "Only 1 bronze ?\nIt sounds like scamming...", None],
            ["Explorat", "Really ? You know, it's the hamlet currency\nand it has higher value than you think...\nyou can for sure buy many things with...", None],
            ["You", "Then if it's so precious\nwhy offer it to an \"unknown\"\nand not the ruby for instance ?", None],
            ["Explorat", "Because ehm...\nyou need it to prosper in this place !\nNo one here buys in gold only in bronze !\nYou're gonna stay here several days right ?", None],
            ["You", "(u bastard)\nYes I guess.\nWho can sell me anything for bronze ?", None],
            ["Explorer", "You can check the lumberjack.\nHe is selling wood.", None],
        ]),
        (6,6, 2,1, None),
        (17,1, 11,1, [
            ["Explorer", "Anyways, we still have that problem.", None],
            ["Explorer", "As you know, we would like to use the mines,\nbut they are strangely infested\nwith some... animals. Harmful ones.", None],
            ["Explorer", "I want you to find how they appeared\nand to get rid of them.", None],
            ["Explorat", "Bring 1 bronze and I'll give you\nthe key to enter.", None],
            ["Explorer", "Be careful in here.\nAlso, I remember that there is\na way through a second level.\nMaybe it's from there ?", None],
            ["Explorer", "I put all my hope in you.\nGood luck.", None],
            ["You", "Wow not so fast lmao.\nR U KIDDING ME ?!\nYou make me PAY to help you ?!?!", None],
            ["Explorat", "(gimme my bronze back)\nI have to make sure you are enough prepared.\nIt's just to verify if you have minimal resources.", None],
            ["You", "(you mf*r)\nI guess it's fine.", None],
        ]),
        (0,6, 1,1, [
            ["You", "So... I can get that ruby now !", None],
            ["Explorat", "Yes, for 6 gold still.", None],
            ["You", "Wat I saved your f*king ham lett\nand you don't atleast reduce the price ?!\nIt's you who should pay me 6 gold.", None],
            ["Explorat", "Nothing is free in life kid.\n(plus I want my gold back >D)", None],
            ["You", "(wait until i knock you out)\nlet's say 3 gold.", None],
            ["Explorer", "You forgot that I said no negociation ?!\n(and that I knocked you out in 5sec also)", None],
            ["You", "(I'm at this to bring a gun)\nOk I give up. 6 gold.", None],
        ]),
    ],
    "quest": [
        # BARN
        [
            ["Hey, can I ask you something ?",
             "Our old barn needs to be demolished.\nIt's few steps at the north east."],
            ("abandoned", (17,1), "Breaking barn", "That old barn belongs to the past."),
            ["You did it ? Great job !", "All work deceives salary."]
        ],
        # ERADICATE
        [
            ["The mines are filled of harmful animals.\nPlease find a way to get rid of them.","There is a passage to another level somewhere.\nYou should maybe check it ?"],
            ("queen", (0,1), "Eliminate mine animals", "I hope I don't have to kill them 1 by 1..."),
            ["Are you sure they are gone now ?",
             "No matter if there remains a few.\nHuge thanks for your help.",
             "This time, I can't refuse you a hefty price.",
             "You are saving our hamlet ;)"]
        ]
    ],
    "tutorial": [
        ["Explorer", f"Watch the tutorial again ?", {
            "Yes": pnj.world.tutorial,
            "No": None
        }]
    ]
},
"blacksmith" : {
    "_panel": [
        [
            ["Blacksmith", "Hi dude how is it ?", None],
            ["You", "I'm good, thank you.", None],
            ["Blacksmith", "Need anything ?", None],
            ["Blacksmith", "I'm always ready to help you.", None],
            ["You", "Thanks. You're cooler than that explorer.", None],
            ["Blacksmith", "Really ? He is that bad ?", None],
            ["You", "He's a little irritating.", None],
        ],
        [
            ["Blacksmith", "What's your choice ?", None],
            ["You", "I'm not sure...", None],
            ["Blacksmith", "That's alright.", None],
            ["Blacksmith", "It's a cozy game after all.", None],
        ]
    ],
    "talk": [
        [
            ["You", "Hello. I'm just passing by.", None],
            ["Blacksmith", "Hi dude.\nI'm the blacksmith.\nI provide tools for the hamlet.", None],
            ["You", "You know where I can find a ruby ?", None],
            ["Blacksmith", "Ask this guy at the right.", None],
            ["You", "uhm... ok.", None],
            ["You", "Thank you !", None],
            ["Blacksmith", "You're welcome.\nCome to me if you have any problem.", pnj.complete_talk],
        ],
        [
            [None, "Talk to the blacksmith.", {

            "Joke": [
                ["You", "Hello ...\n(choose a joke)", {
                    'Volcano': [
                        ["You", "What does a mountain\nsays to a volcano ?", None],
                        ["You", "No smoking.", None],
                        ["Blacksmith", "What does an NPC\nsays to this walking sh*t ?\nNo lame jokes.", None],
                    ],
                    'House': [
                        ["You", "The green house is at the left.", None],
                        ["You", "The blue house is at the right.", None],
                        ["You", "The red house is behind.", None],
                        ["You", "Where is the white house ?", None],
                        ["Blacksmith", "answer?", None],
                        ["You", "At washington.", None],
                        ["Blacksmith", "uhm..ok.", pnj.complete_talk],
                    ],
                }]
            ],

            "Riddle": [
                ["You", "Hello ...\n(choose a riddle)", {
                    'Spaceship': [
                        ["You", "What does a spaceship with an illum-", None],
                        ["Blacksmith", "Wait I have a question for you.", None],
                        ["Blacksmith", "You drop from the window of\nthe 3rd floor of a cruise ship\na feather and a lead ball\nWhich hit the land first ?", {
                            'Lead': [["Blacksmith", "Are you sure ?", None]],
                            'Both': [["Blacksmith", "There is no effort.", None]],
                            'None': [["Blacksmith", "Yes because they land on water !", pnj.complete_talk]],
                        }],
                    ],
                    'Gold': [
                        ["You", "Someone buy 1 gold\nat the price of 2 golds.\nWhy ?", None],
                        ["Blacksmith", "???", None],
                        ["You", "BCZ HE'S STUPID", None],
                        ["Blacksmith", "-_- so are you", None],
                    ],
                    'File': [
                        ["You", "3 people walk in single file.", None],
                        ["You", "The first one says\nhe doesn't see anyone before him.", None],
                        ["You", "The second one says\nhe see 1 person before him.", None],
                        ["You", "The third one says\nhe see 2 person before him.", None],
                        ["You", "The fourth one says\nhe doesn't see anyone before him.", None],
                        ["You", "How is this possible ?", None],
                        ["Blacksmith", "uhm...he is...", None],
                        ["You", "he lied.", None],
                        ["Blacksmith", "...", None],
                        ["Blacksmith", "yes that's logic after all.", pnj.complete_talk],
                    ],
                }]
            ],

            }],
        ]
    ],
    "trade": [
        # I1,A1, I2,A2, dialog
        (7,2, 3,1, None),
        (7,3, 4,1, None),
        (7,3, 5,1, None),
        (7,6, 17,1, None),
    ],
    "quest": [
        # § (stone)
        [
            ["Need 10 more rocks .."],
            ((2,10), (7,1), "Bring 10 rocks ?", "I don't know why he needs that..."),
            ["Take this in return."]
        ],
        # § (or: IMPORTANT!)
        [
            ["Hi, I'd like to grow fruits too.", "Provide me a watering can please."],
            ((15,1), (0,1), "Offer a watering can.", "He also want to compete with fisherman xD"),
            ["This quest is just a template.", "So take this gold even if it's too much."]
        ]
    ],
    "repair": pnj.repair
},
"fisherman": {
    "_panel": [
        [
            ["Fisherman", "Good day, how do you fare?", None],
            ["You", "What does that mean ?", None],
            ["Fisherman", '"hello how are you" but more stylish.', None],
            ["You", "Oki I'm great.", None],
            ["Fisherman", "No. Say: Indeed, I am well.", None],
            ["You", "Indid, eye am wel.", None],
            ["You", "My turn: say \"ref mami\" backwards.", None],
            ["Fisherman", "Stop it or I'll ban you.", None],
            ["You", "Okay. Sorry.", None],
        ],
        [
            ["Fisherman", "What do you desire ?", None],
            ["You", "A triple tier chocolate banana cake.", None],
            ["Fisherman", "Please choose among what we have.", None],
            ["You", "You only have rocks.", None],
            ["Fisherman", "If you're not satisfied, please go out.", None],
            ["You", "No let me choose. (choose lmao)", None],
            ["Fisherman", "Then it's okay. Don't be rushed.", None],
            ["Fisherman", "It's a comfortable game after all.", None],
        ]
    ],
    "talk": [
         [
            ["You", "Hello. I'm just passing by.", None],
            ["Fisherman", "Hi dude.\nI'm the fisherman.\nI ... fish.", None],
            ["You", "You fish.", None],
            ["Fisherman", "I fish.", None],
            ["You", "You know where I can find a ruby ?", None],
            ["Fisherman", "The explorer has one. Why ?", None],
            ["You", "It's logic right ?!", None],
            ["You", "To have it old retard\ncan you think 2 seconds ?!", None],
            ["Fisherman", "... please not be so rude.", pnj.complete_talk]
        ],
        [
            [None, "Talk to the fisherman.", {

            "Joke": [
                ["You", "Hello ...\n(choose a joke)", {
                    'Bear': [
                        ["You", "What would bears be without bees-", None],
                        ["Fisherman", "Dude you found it on google", None],
                        ["You", "- Ears !", None],
                    ],
                    'Skeleton': [
                        ["You", "Why do a skeleton\ndon't kill his murderer ?", None],
                        ["Fisherman", ".. coz he's dead ..", None],
                        ["You", "COZ HE DON'T HAVE THE BALLS", None],
                        ["Fisherman", "...", None],
                        ["Fisherman", "Brillant !", pnj.complete_talk],
                    ],
                }]
            ],

            "Riddle": [
                ["You", "I have a question-", None],
                ["Fisherman", "I have one too.", {
                    "Yours": [
                        ["You", "What is the capital of France ?", None],
                        ["Fisherman", "Is that really a question ?", None],
                        ["You", "It's \"F\"\ncoz it's capital letter", None],
                        ["Fisherman", "You know what also start by F ?!", None],
                        ["Fisherman", "F*CK OFF", None],
                    ],
                    "His":  [
                        ["Fisherman", "You just doubt the 2nd. You are:", {
                            "1st": [["Fisherman", "Can you think 2 seconds ?!", None]],
                            "2nd": [["Fisherman", "Exact ! You're smarter than\nyour face suggests.", pnj.complete_talk]],
                            "last":[["Fisherman", "You are the least of the idiots.", None]],
                        }]
                    ]
                }]
            ],

            }],
        ]
    ], 
    "trade": [
        # I1,A1, I2,A2, dialog
        (7,3, 8,1, None),
        (9,4, 2,6, None),
        (10,3, 2,6, None),
        (16,3, 2,6, None),
    ],
    "quest": [
        # Fish command
        [
            ["Hey, can I ask you something ?",
             "We need 10 fish to complete the batch.","I'm quite busy with financial things..."],
            ((9,10), (2,3), "10 more fish", "He does not looks like that busy..."),
            ["There we go !\nOur third fish order is complete !",
             "Ehm...\n(grab pebbles from his pocket)\nHere is your prize."]
        ],
        # Chicken command
        [
            ["Hi, we have an emergency order.","A butchery is asking us 20 chicken\nbut as you know our barn is broken.","But you can hunt them !\nIf you do it I'll give you a big prize."],
            ((10,20), (0,1), "Emergency 20 chicken", "He could just cancel..."),
            ["(look the rotten chicken)\nIt's unsaleable...",
             "Really ? Thanks man ! Take this. ...",
             "I can't believe I just gave you so much in return.",
             "Ah yes it's just a quest template."]
        ],
    ],
    "how to fish": [
        ["Fisherman", f"Do you want me\nto teach you how to fish ?", {
            "Yes": [
                ["Fisherman","First, go to the lake.",None],
                ["Fisherman","Then, keep pressing\nleft mouse button.",None],
                ["Fisherman","When a bubble appears\nstop pressing.",None],
                ["Fisherman","When you have atleast 4 fish\ngo trade them to me.",None],
            ],
            "No": None
        }]
    ]
},
"miner": {
    "_panel": [
        [
            ["Miner", "How's it going?", None],
            ["You", "I'm doing well.", None],
            ["Miner", 'Really ? Great !', None],
            ["You", "I just said i'm fine.", None],
            ["Miner", " I mean how's it going with the queen ?", None],
            ["You", "Uhm... I see.", None],
        ],
        [
            ["Miner", "What's your choice?", None],
            ["You", "You don't have any gun ?", None],
            ["Miner", "I would like to.", None],
            ["Miner", "Anyways please buy something.", None],
            ["Miner", "I need bronze for my comeback.", None],
            ["Miner", "Whatever, it's at your own pace.", None],
            ["Miner", "It's a serene game after all.", None],
        ]
    ],
    "talk": [
        [
            ["Miner", "...", None],
            ["Miner", "Who are you ?!", None],
            ["You", "You aren't from the hamlet ?", None],
            ["Miner", "Answer me ?!", None],
            ["You", "Chill dude\nI'm their guest.", None],
            ["You", "So now.\nWho the f* are you ?", None],
            ["Miner", "I'm the former chief of the hamlet.", None],
            ["You", "You left right ?", None],
            ["Miner", "Yes. Because I got depressed.\nBut I soon felt nostalgic.", None],
            ["Miner", "I wanted to comeback,\nBut not just like that.\nA surprise comeback !", None],
            ["Miner", "I don't want to come empty-handed.\nI have to bring something.\nTo appear legitimate.\n(and be the leader again :D)", None],
            ["Miner", "I plan to make fortune with iron mining.\nBut I knew they looked for the mines.", None],
            ["Miner", "So I brought some wild animals\nto scare them the time that\nI make enough money\nto restore the barn.", None],
            ["Miner", "But soon a queen and her family joined them.\nThey got a new home.", None],
            ["Miner", "I lost control of the situation.\nI can't comeback like that !", None],
            ["Miner", "And that's when you come, fellow guest,\nYou can help me killing that queen !", None],
            ["Miner", "...", None],
            ["Miner", "I dream to see my barn again.\nI can't wait !", None],
            ["Miner", "...", pnj.complete_talk]
        ],
        [
            [None, "Talk to the miNERD.", None],
            ["You", "the miNERD ?!.", None],
            ["M1N3RD", "H3110.", pnj.minerd],
        ]
    ], 
    "trade": [
        # I1,A1, I2,A2, dialog
        (12,3, 7,1, None),
        (17,1, 13,1, None),
        (17,1, 14,1, None),
        (17,6, 0,1, [
            ["You", "6 bronze one gold ?!", None],
            ["Miner", "Yes I need bronze.", None],
            ["You", "Can we negociate ?", None],
            ["Miner", "If not 6 then 9. It's my last offer.", None],
            ["You", "That's not negociation.", None],
        ]),
    ],
    "quest": [
        # Fish
        [
            ["I'm hungry.","I remember lumberjack started an apple farm.\nI never took it serious...", "Anyways, can you bring me some apples ?\n[bring 10 of them.]"],
            ((16,10), (7,6), "Gather 10 apples", "That miner should be starving..."),
            # Thank dialog
            ["A human can survive 1 month without eating.\nI didn't eat for 2 days.",
             "You didn't have to hurry this much.",
             "Anyways let's eat a fresh one :)",
             "I've eaten chicken all my life..."]
        ],
        # Queen
        [
            ["Hey, we still have to kill that monster.",
             "I know it's dangerous but please help me.\nI have no other solution."],
            ("queen", (0,1), "Kill the queen", "A huge beast is standing near."),
            ["What was that ?!",
            "You killed her ! That's insane !",
            "Thank you immensly for your help.\nTake this 1 gold as a deceived prize.",
            "Did you saw ? The racoons suddenly faded off.",
            "Haha issue solved ! A few more golds to farm\nand I'm back ! All my gratitude.",
            ]
        ]
    ],
    "fight queen": [
        ["Miner", f"Do you want to learn\nhow to fight ?", {
            "Yes": [
                ["Miner","So.",None],
                ["Miner","The mines are swarmed with those animals.",None],
                ["Miner","They charge you when they see you\nbut you can dodge them easily.",None],
                ["Miner","Hitting them hurts them\nans can make them flee.",None],
                ["Miner","You can either use\na melee weapon or a slingshot.",None],
                ["Miner","Slingshot use rocks.\nTo farm them in quantity, use a hammer.\nHammer can also break iron ores.",None],
                ["Miner","The queen is different.",None],
                ["Miner","Man you have to see it, she's colossal.",None],
                ["Miner","She is harmless while you stay calm.",None],
                ["Miner","But hitting, shooting or going too near\nprovocates her.\n(also going too near damages you!)",None],
                ["Miner","Once you provocate her,\nshe attacks you until you die.",None],
                ["Miner","That beast charges straight at you\nand you must avoid it each time.",None],
                ["Miner","If you enter the gray area, it attacks you\nand from then on it's difficult to escape.",None],
                ["Miner","To attack it, pass behind it\nand strike the red zone.",None],
                ["Miner","Also, you simply can't\nhurt her with a slingshot.\nOnly melee weapon are harmful enough.\nOr a gun but it's illegal to have guns.",None],
                ["Miner","To see the zones, provocate her.\nThe safest way is by shooting.\nYou can dodge her easier.",None],
                ["Miner","That's all, fellow.",None],
                ["Miner","Please kill that monster.",None],
            ],
            "No": None
        }]
    ]
},
"lumberjack": {
    "_panel": [
        [
            ["Lumberjack", "How ru ?", None],
            ["You", "Uhm.. I'm good.", None],
            ["Lumberjack", 'wat du u want ?', None],
            ["You", "Lemme think a second.", None],
            ["Lumberjack", 'its bin 1 cekond all redi.', None],
            ["You", "Ok so lemme 1 hour.", None],
            ["Lumberjack", 'it fil laiq its bin 1 oure.', None],
            ["You", "It's been 1 minute only.", None],
            ["Lumberjack", 'dicyd pliz.', None],
        ],
        [
            ["Lumberjack", "lu king 2 buy som thing ?", None],
            ["You", "Please lemme think...", None],
            ["Lumberjack", "wat du u thinq abawt ze wud ?", None],
            ["Lumberjack", "I bronz iz uorth 6x6=36 wud.", None],
            ["Numberjack", "Im giving 8O its a golden dil.", None],
            ["You", "It's 6x6x6=216 wood asshole.", None],
            ["Numberjack", "Wut ?", None],
            ["Lumberjack", "wat ever chooz trenkilli.", None],
            ["Lumberjack", "Its a piss full gamme aftere aul.", None],
        ]
    ],
    "talk": [
        [
            ["You", "Hello. I'm just passing by.", None],
            ["Lumberjack", "Huh ?\nIm ze lumberjak.\ni furnich wud 4 ze hamlet.", None],
            ["You", "(what kind of language is that?!)\nWhere can I get a ruby ?", None],
            ["Lumberjack", "At ze jewelry.", None],
            ["You", "Don't try to fool me.\nI know from reliable sources you have one.", None],
            ["Lumberjack", "Wat r ur \"sources\" ?", None],
            ["You", "confidential", None],
            ["Lumberjack", "hmm we du hav 1 but we wont giv u.", None],
            ["You", "too bad :C", None],
            ["You", "anyways.\nI'm gonna stay here a while.\nNice to meet you.", None],
            ["Lumberjack", "Finely u respekt mi.", None],
            ["You", "(sucks him for his trades)\nOf course I respect you !\nAnd wow ! You have a farm ??", None],
            ["Lumberjack", "Yes! I hav a smal orkard.", None],
            ["Lumberjack", "I hop 2 enhans it and\nturn it in2 a gr8 farm.", None],
            ["Lumberjack", "We can sel aples and mak 4tun with zat !", None],
            ["Lumberjack", "(I want to compit with zat mershant!!!)", None],
            ["Lumberjack", "I can allso cher it to u 4 1 bronz.", None],
            ["You", "(nice) thank you for your offer !", pnj.complete_talk],
        ],
        [
            ["Lumberjack", "Helo du u want som advices ?", {
                "Yes": [
                    ["Lumbardjack", "Okay.\nInitially, it is possible to fell multiple trees\nsimultaneously by correctly positioning your tool.\nThis capability offers significant efficiency,\ndoes it not ?", None],
                    ["You", "(since when he learned to talk ??)\nGreat for sure !", None],
                    ["Lumbardjack", "Subsequently, you better refrain from purchasing\nbronze when lacking iron and facing tool damage.", None],
                    ["Lumbardjack", "It would be such a cruelty to be left\nwith no recourse but to forfeit bronze\nin exchange for wood, wouldn't you agree ?", None],
                    ["You", "(what the f* ?!)\nYeah completely.", None],
                    ["Lumbardjack", "I further add, strictly between us,\nthat henceforth you must never again\nexchange gold for 1 bronze under any circumstances.\nIt is an unequivocal swindle.", None],
                    ["Lumbardjack", "Lastly, do not endeavor to acquire\nthe requirement for trades directly.\nRather, emphasis should be placed on\nundertaking quests to unlock trading opportunities.", None],
                    ["Lumbardjack", "After all, attempting to amass six gold solely\nthrough the use of an axe is stupidly laborious,\ndoes it not ?", None],
                    ["Lumbardjack", "What am I saying?\nNo one here is inclined to sell gold anyway.", None],
                    ["You", "I see. Thank you so much for your advices.", None],
                    ["Dumberjack", "U well ccom!\nzat goz str8 2 mai hurt!\n*hert", None],
                    ["You", "... (-_-)", None],
                    ["Lumberjack", "besides zat, i so ze farmer last nite.", None],
                    ["Lumberjack", "u now, ze guye wu left...", None],
                    ["Lumberjack", "im not jokin\ni think he hide som wher", None],
                    ["Lumberjack", "maybi he plan tu go bak ?", None],
                    ["Lumberjack", "...", pnj.complete_talk],
                ]
            }],
        ]
    ], 
    "trade": [
        # I1,A1, I2,A2, dialog
        (17,1, 6,80, [
            ["You", "(alone) man it's dumberjack not lumberjack xD", None],
        ]),
        (2,6, 7,1, None),
        (0,2, 0,1, [
            ["You", "Wait, what is that new trade ?!", None],
            ["Lumberjack", "A template trade.", None],
        ]), # §
        (17,1, 15,1, None),
    ],
    "quest": [
        # Find miner
        [
            ["yesterday i so ze farmer watching us.","i think he is around hir.\ncan u find im ?"],
            ("dungeon", (10,1), "Find the farmer", "He might be... around ?"),
            ["u found im ? i new he was hir."]
        ],
        # Repair barn
        [
            ["i so zat barn is distr0yd.","i dont now which mfer did zat\nbut wi hav to ristor it fast\nif farmer see zat..."],
            ((6,100), (0,1), "Restore barn (100 wood)", "What have I done ?!"),
            [
                "thank u. wiz zat i choud bi abl to ristor it.",
                "[A few moments later...]\n[...]\nfinaly don.",
                "wi can reciv hime in ani tim now.",
            ]
        ]
    ],
},
}[pnj.name]
