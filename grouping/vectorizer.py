import re, sys

class linkedObject:
    def __init__(self, itemText, typeIndex):
        self.linkedObjects = []
        self.itemTypeIndex = None
        self.itemText = ""
        self.itemID = None
        self.visited = False
        
        self.itemText = itemText
        self.itemTypeIndex = typeIndex
        
    def addLink(self, linkedObjectInstance):
        self.linkedObjects.append(linkedObjectInstance)
        linkedObjectInstance.linkedObjects.append(self)
        
    def printLinks(self):
        print "links are for"
        for links in self.linkedObjects:
            print "   -->" + links.itemText
            
    def printText(self):
        print self.itemText
        
class vectorizedObject:
    def __init__(self, linkedObjectPassed, numberOfTypes, id):
        self.identifier = id
        traversalStack = []
        currentLinkedObject = linkedObjectPassed

        while True:
            currentLinkedObject.itemID = self.identifier
            currentLinkedObject.visited = True
            
            nextLinkFound = False
            for link in currentLinkedObject.linkedObjects:
                if not link.visited:
                    traversalStack.append(currentLinkedObject)
                    currentLinkedObject = link
                    nextLinkFound = True
                    break
            
            if not nextLinkFound:
                if not traversalStack:
                    break
                currentLinkedObject = traversalStack.pop()
        
        
def parseHeader(fd):
    return fd.readline().split(",")

def parseLines(fd):
    lineList = fd.readlines()
    objectList = []
    for line in lineList:
        objectList.append(line.strip().split(","))
    return objectList

def populateDicts(objectList, objectDicts, dictionaryTypeLocation):
    for line in objectList:
        lastItemFound = None

        for index, item in enumerate(line):
            if len(item) == 0:
                continue
            if dictionaryTypeLocation[index] != None:
                dictionaryType = objectDicts[dictionaryTypeLocation[index]]
                if item not in dictionaryType:
                    newLinkedItem = linkedObject(item, index)
                    dictionaryType[item] = newLinkedItem
                if lastItemFound:
                    dictionaryType[item].addLink(lastItemFound)
                lastItemFound = dictionaryType[item]
                    
            else:
                newLinkedItem = linkedObject(item, index)
                if lastItemFound:
                    newLinkedItem.addLink(lastItemFound)
                lastItemFound = newLinkedItem
                
def cleanAllPhoneNumbers(objectList, objectTypes):
    phoneNumberTypeRegex = "[pP]hone"
    phoneColumns = [offset  for offset, type in enumerate(objectTypes) if re.search(phoneNumberTypeRegex, type)]
    for row in objectList:
        for offset in phoneColumns:
            row[offset] = cleanPhoneNumber(row[offset])
            
def cleanPhoneNumber(number):
        match = re.match("1?.*(\d{3}).*(\d{3}).*(\d{4})",number)
        if match:
            return "".join(match.group(1,2,3))
        else:
            return ''

def listToCSV(list):
    return ",".join(list) + "\n"

def main():
    fd = open(sys.argv[1],"rU")
    objectTypes = parseHeader(fd)
    objectList = parseLines(fd)
    print objectTypes
    
    objectDicts = []
    colsToMatchOn = []
    defaultTypesRegex = ["[pP]hone", "[eE]mail"]
    typeRegexes = defaultTypesRegex
    
    if len(sys.argv) > 2:
        typeRegexes = sys.argv[2:]
    
    objectDicts = [{} for x in typeRegexes]
    dictionaryTypeLocation = []
    
    for type in objectTypes:
        for dictOffset, typeRegex in enumerate(typeRegexes):
            if re.search(typeRegex, type):
                dictionaryTypeLocation.append(dictOffset)
                break
        else:
            dictionaryTypeLocation.append(None)

    cleanAllPhoneNumbers(objectList, objectTypes)
    populateDicts(objectList, objectDicts, dictionaryTypeLocation)

    id = 0
    for index, dictType in enumerate(objectDicts):
        for item in dictType:
            linkedItem = dictType[item]
            if not linkedItem.visited:
                it = vectorizedObject(linkedItem, len(objectTypes), id)
                #linkedItem.printLinks()
                id += 1

    fdWriter = open("testOut.txt","w")
    for list in objectList:
        for index, item in enumerate(list):
            if item and dictionaryTypeLocation[index] != None:
                fdWriter.write( "id is :" + str(objectDicts[dictionaryTypeLocation[index]][item].itemID) + " ")
                fdWriter.write( listToCSV(list))
                break;
        else:
            fdWriter.write("id is :" + str(id) + " " + listToCSV(list))
            id += 1
    fdWriter.close()
main()