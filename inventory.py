
class Inventory:
    def __init__(self, items={}) -> None:
        self.items = items

    def save(self):
        return self.items

    def add(self, item, amount=1):
        if item in self.items:
            self.items[item] += amount
        else:
            self.items[item] = amount
    
    def has(self, item, amount=1):
        return self.items.get(item, 0) >= amount
    
    def remove(self, item, amount=1):
        self.items[item] -= amount
        if self.items[item] < 0:
            raise SystemError("INVENTORY REMOVE TOO MUCH ITEM")
        if self.items[item] == 0:
            del self.items[item]