import math
import pygame as pg

# Time
def timeout(time,dura): return (pg.time.get_ticks()-time) >= dura

timers = []

class Timer:
    def __init__(self, duration, callback=None):
        self.duration = duration
        self.callback = callback
        self.start_time = 0
        self.active = False

    def activate(self):
        self.active = True
        self.start_time = pg.time.get_ticks()
        return self

    def deactivate(self):
        self.active = False
        self.start_time = 0

    def toggle(self):
        if self.active: self.deactivate()
        else: self.activate()

    def time(self, default=0):
        if self.active: return (pg.time.get_ticks()-self.start_time)
        return default
    
    def timesec(self, default=0, reverse=False):
        if self.active:
            time = self.time()
            if reverse: time = self.duration-time
            return math.floor(time/1000) if not reverse else math.ceil(time/1000)
        else:
            return default

    def percent(self, default=1):
        if self.active: return self.time()/self.duration
        return default

    def update(self):
        if self.active:
            if timeout(self.start_time, self.duration):
                self.deactivate()
                if self.callback:
                    self.callback()

def wait(time):
    def inner(func):
        timers.append((pg.time.get_ticks(), time*1000, func))
    return inner

def timers_update():
    global timers
    to_delete = []
    for timer in timers:
        start, dura, callback = timer
        if pg.time.get_ticks() - start >= dura:
            callback()
            to_delete.append(timer)
    timers = list(filter(lambda t: t not in to_delete, timers))


class Transition(Timer):
    def __init__(self, dura, dura2=None, callmid=None, callend=None):
        super().__init__(dura, self.call)
        self.dura, self.dura2 = dura, dura2 or dura
        if callmid==True: callmid = self.activback
        self.callmid, self.callend = callmid, callend
        self.backwards = False
        self.on = False

    def deactivate(self):
        super().deactivate()
        self.on = False

    def call(self):
        # Normal
        if not self.backwards:
            self.on = True
            if self.callmid: self.callmid()
        # Backwards
        elif self.callend:
            self.callend()

    def percent(self, max=None):
        if self.active:
            x = min(1, self.time()/(max or self.duration))
            return x if not self.backwards else 1-x
        else:
            return self.on
    
    def toggle(self):
        if (self.active or self.on) and not self.backwards:
            self.activback()
        else:
            self.activate()

    def activate(self, backwards=False):
        self.backwards = backwards
        if backwards: self.on = False
        self.duration = (self.dura, self.dura2)[backwards]
        super().activate()

    def activback(self): self.activate(1)

    def activate_var(self, var, old):
        if var and not old: self.activate()
        elif old and not var: self.activate(1)
        