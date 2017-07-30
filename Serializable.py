class Serializable(object):
    def save(self):
        raise NotImplementedError("Not implemented method Serializable::save")
    def restore(self, obj):
        raise NotImplementedError("Not implemented method Serializable::restore")
