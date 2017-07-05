import json
import pandas as pd


class JSONFlattener(object) :

    def __init__(self, jsonString) :
        self.__reset()
        self.jsonString = jsonString

    def __reset(self) :
        self.__jsonString = None
        self.__flattenedJsonData = None
        self.__flattenedKeys = None

    def __get_jsonString(self) :
        return self.__jsonString

    def __set_jsonString(self, jsonString) :
        self.__jsonString = jsonString

    def __get_flattenedKeys(self) :
        if self.__flattenedKeys is None :
            warnings.warn('Data have not yet been flattened. Returning None.', category=UserWarning)
        return self.__flattenedKeys

    def __unpackParsedJson(self, parsedJson, currentName, reset=False) :
        if reset :
            self.__currentState = []
        if isinstance(parsedJson, list) :
            # OPTION 1: Parsed JSON is a list-type - recursively process each subelement, appending the element index to the name
            for op in (self.__unpackParsedJson(listElement, '{}.{}'.format(currentName, listIndex)) for listIndex, listElement in enumerate(parsedJson)) :
                pass
            return self.__currentState
        elif isinstance(parsedJson, dict) :
            # OPTION 2 : Parsed JSON is a dict-type - recursively process each subelement, appending the element key to the name
            for op in (self.__unpackParsedJson(dictElement, '{}.{}'.format(currentName, dictKey)) for dictKey, dictElement in parsedJson.items()):
                pass
            return self.__currentState
        elif parsedJson is not None :
            # OPTION 3: Parsed JSON is a POD - return a name-value pair as a tuple
            return self.__currentState.extend([(currentName, parsedJson)])
        else :
            return self.__currentState

    def __upackedListToSeries(self, parsedList):
        return pd.Series({key : value for (key, value) in parsedList})

    def __unpackJson(self, prefix = '') :
        print('Flattening JSON...')
        parsedJson = json.loads(self.jsonString)
        self.__currentState = None  # Initialize to None as this might highlight semantic errors
        self.__flattenedJsonData = self.__upackedListToSeries(self.__unpackParsedJson(parsedJson, prefix, True))
        #  Save a list of all flattened keys
        self.__flattenedKeys = list(self.__flattenedJsonData.index)
        print('Done.')

    #  API DEFINITIONS

    flattenedKeys = property(__get_flattenedKeys)
    jsonString = property(__get_jsonString, __set_jsonString)

    def flatten(self, prefix = '') :
        if self.__flattenedJsonData is None :
            self.__unpackJson(prefix)
        return self.__flattenedJsonData
