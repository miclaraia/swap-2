import warnings
import csv
import json
import pandas as pd


class CsvDumpParser(object) :

    def __init__(self, dumpFile) :
        self.dumpFile = dumpFile
        self.__reset()
        self.__columnHeadings()

    def __reset(self) :
        self.__parsedCsvData = None
        self.__flattenedCsvData = None
        self.__flattenedKeys = None

    def __get_dumpFile(self) :
        return self.__dumpFileName

    def __set_dumpFile(self, dumpFile) :
        self.__dumpFileName = dumpFile
        self.__columnHeadings()

    def __columnHeadings(self) :
        self.__jsonKeys = []
        self.__nonJsonKeys = []
        with open(self.__dumpFileName, 'r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            row = next(reader)
            for key, value in row.items():
                try :
                    # ignore numeric types
                    parsedValue = float(value)
                    self.__nonJsonKeys.append(key)
                except :
                    try :
                        parsedValue = json.loads(value)
                        self.__jsonKeys.append(key)
                    except :
                        #ignore types that cannot be interpreted as JSON
                        self.__nonJsonKeys.append(key)

    def __get_jsonKeys(self) :
        return self.__jsonKeys

    def __get_nonJsonKeys(self) :
        return self.__nonJsonKeys

    def __readCsv(self) :
        print('Parsing CSV file...')
        self.__parsedCsvData = pd.read_csv(self.dumpFile)
        print('Done.')

    def __get_parsedCsv(self) :
        if self.__parsedCsvData is None :
            self.__readCsv()
        return self.__parsedCsvData

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

    def __unpackJsonColumns(self, skipColumns = [], rowRange = (0, -1)) :
        print('Flattening JSON columns...')
        print('Will not flatten {}.'.format(', '.join(skipColumns)))
        self.__flattenedCsvData = self.__parsedCsvData.iloc[rowRange[0]:rowRange[1]]
        for column in list(set(self.jsonKeys) - set(skipColumns)) :
            self.__currentState = None  # Initialize to None as this might highlight semantic errors
            applied = self.__flattenedCsvData[column].apply(json.loads).apply(self.__unpackParsedJson, args=(column, True)).apply(self.__upackedListToSeries)
            self.__flattenedCsvData = pd.concat([self.__flattenedCsvData, applied], axis=1)
        #  Save a list of all flattened keys
        self.__flattenedKeys = self.__flattenedCsvData.columns.values
        print('Done.')

    #  API DEFINITIONS

    flattenedKeys = property(__get_flattenedKeys)
    dumpFile = property(__get_dumpFile, __set_dumpFile)
    parsedCsv = property(__get_parsedCsv)
    nonJsonKeys = property(__get_nonJsonKeys)
    jsonKeys = property(__get_jsonKeys)

    def getUnpackedData(self, skipUpackingFor = ['subject_data'], rowRange = (0, -1)) :
        if self.__flattenedCsvData is None :
            self.__unpackJsonColumns(skipColumns = skipUpackingFor, rowRange = rowRange)
        return self.__flattenedCsvData
