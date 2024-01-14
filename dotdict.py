class superlist(list):
    def __getitem__(self, item):
        to_ret = super().__getitem__(item)
        if isinstance(to_ret, dict):
            return dotdict(to_ret)
        return to_ret
    

class dotdict(dict):
    def __getattr__(self, attr):
        to_ret = self.get(attr)
        if isinstance(to_ret, dict):
            return type(self)(to_ret)
        elif isinstance(to_ret, (list, tuple)):
            return superlist(to_ret)
        return to_ret
    
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    