from util.support import *

def draw_circle(p,w):
    pg.draw.circle(w.display, p['color'], p['pos']-w.offset, p['radius'], p.get('width',0))

def draw_rect(p,w):
    pg.draw.rect(w.display, p['color'], (p['pos']-w.offset,p['size']))

def draw_image(p,w):
    w.display.blit(p['image'], p['image'].get_rect(center=p['pos']-w.offset))

def timeout(p, dura):
    def inner(func):
        if (pg.time.get_ticks() - p['time']) >= dura:
            func()
    return inner


class Particle:
    def __init__(self, **defargs):
        particles.append(self)
        self.particles = []
        self.to_delete = []
        self.defagrs = defargs

        self.init_func = None
        self.update_func = None
        self.draw_func = None
    
    def __iter__(self):
        return iter(self.particles)
        
    def new(self, pos, *a, **kw):
        p = {'pos':pos,'time':pg.time.get_ticks()}|self.defagrs
        if not self.init_func: p |= kw
        else: p |= self.init_func(p, *a,**kw)
        if 'group' in p:p['group'].append(p)
        self.particles.append(p)
            
    def init(self, func): self.init_func = func
    
    def update(self, func): self.update_func = func
        
    def draw(self, func): self.draw_func = func

    def delete(self, p):
        self.to_delete.append(p)
        if 'group' in p:
            p['group'].remove(p)
        
particles:list[Particle] = []


def draw(w, *groups):
    for pc in (groups or particles):
        for p in pc:
            pc.draw_func(p, w)

def update(w):
    for pc in particles:
        for p in pc.particles:
            pc.update_func(p, w)

        pc.particles = [p for p in pc.particles if p not in pc.to_delete]
        pc.to_delete.clear()