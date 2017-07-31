class Serializable(object):
    def save(self):
        raise NotImplementedError("Not implemented method Serializable::save")
    def restore(self, obj):
        raise NotImplementedError("Not implemented method Serializable::restore")

    def toJson(self):
        raise NotImplementedError("Not implemented method Serializable::save")
    def restoreFromJson(self, jsonObject):
        raise NotImplementedError("Not implemented method Serializable::restoreFromJson")
