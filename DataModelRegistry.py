from PortType import PortType


class TypeConverterItem:
    def __init__(self, model = None, sourceType = None, destinitionType = None):
        self.Model              = model             # -> NodeDataModel
        self.SourceType         = sourceType        # -> NodeDataType
        self.DestinationType    = destinitionType   # -> NodeDataType

class DataModelRegistry:
    def __init__(self):
        self._registeredModelsCategory  = {}        # NodeDataModel to category map -> {(NodeDataModel, QIcon): str}
        self._categories                = set()     # categories set -> {str}
        self._registeredModels          = {}        # node model name to NodeDataModel map -> {str: NodeDataModel}
        self._registeredTypeConverters  = {}        # type converters -> {(str, str): TypeConverterItem}

    def registerModel(self, category, icon, model, isConvertor = False):
        self._categories.add(category)
        self._registeredModelsCategory[(model, icon)] = category
        self._registeredModels[model.name()] = model

        if isConvertor:
            if model.isValidTypeConvertor():
                item = TypeConverterItem(model, model.dataType(PortType.In, 0), model.dataType(PortType.Out, 0))
                self._registeredTypeConverters[(item.SourceType.id, item.DestinationType.id)] = item

    def categories(self):
        return self._categories

    def registeredModelsCategoryAssociation(self):
        return self._registeredModelsCategory

    def create(self, modelName):
        return self._registeredModels.get(modelName)
