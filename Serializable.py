class Serializable(object):
    def toJson(self):
        raise NotImplementedError("Not implemented method Serializable::save")
    def restoreFromJson(self, jsonObject):
        raise NotImplementedError("Not implemented method Serializable::restoreFromJson")
