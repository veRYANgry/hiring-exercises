import re, sys
## Vectorizer takes an input test csv file, matches on columns by supplied regex, and outputs unique Ids for rows
 # that match. The output is in Out.txt of the same local directory. Any columns that match phone will be cleaned to 
 # a 10 digit number if possible and the output will reflect that. --Ryan
 
## Iterator object for the linked Objects. Note this iterator will only iterate once through a list.
class linkedObjectIter:
    def __init__(self, linkedObjectInstance):
        self.traversalStack = []
        self.traversalStack.append(linkedObjectInstance)
    
    def next(self):
        # Find the next link that has not been visited.
        currentStackLinkedObject = None
        while self.traversalStack:
            currentStackLinkedObject = self.traversalStack.pop()
            if not currentStackLinkedObject.visited:
                break
        else: 
            if not self.traversalStack:
                raise StopIteration
        
        self.traversalStack += currentStackLinkedObject.linkedObjects
        currentStackLinkedObject.visited = True
        return currentStackLinkedObject

## Linked list of lists for assigning and linking associated objects.
class linkedObject:
    def __init__(self, itemText):
        self.linkedObjects = []       # List of linkedObject references.
        self.itemText = ""
        self.itemID = None
        self.visited = False          # Used for iterating over the linked list.
        self.itemText = itemText

    ## Link two linkedObjects together.
    #  @param linkedObjectInstance The linked object to link the called object to and from.
    def addLink(self, linkedObjectInstance):
        self.linkedObjects.append(linkedObjectInstance)
        linkedObjectInstance.linkedObjects.append(self)

    ## The iterator for this class. Only iterates once through a linkedObject chain.
    def __iter__(self):
        return linkedObjectIter(self)

    # Print debug below:
    def printLinks(self):
        print "links are for"
        for links in self.linkedObjects:
            print "   -->" + links.itemText

## Parse a standard csv heading and output a list.
#  @param fd The file descriptor of the text input.
#  @return The header a list of strings.
def parseHeader(fd):
    return fd.readline().split(",")

## Parse a standard csv line and output a list of elemenet lists.
#  @param fd The file descriptor of the text input.
#  @return The list a list of strings.
def parseLines(fd):
    lineList = fd.readlines()
    objectList = []
    for line in lineList:
        objectList.append(line.strip().split(","))
    return objectList
    
## Go row by row from a list of strings and insert each one into a dict if it exists while linking each related
#  item together.
#  @param objectList The list of objects from the csv file.
#  @param objectDicts The list of dictionaries for each type to check for same items.
#  @param dictionaryTypeLocation The mapping as a list of objectList element to into the objectDicts list.
def populateDicts(objectList, objectDicts, dictionaryTypeLocation):
    for line in objectList:
        lastItemFound = None  # Used for linking related items (like things in the same line)

        for index, item in enumerate(line):
            if len(item) == 0: # Ignore 0 length strings
                continue
            # Check the dictionary.
            if dictionaryTypeLocation[index] != None: # Check for a dictionary to place items into.
                dictionaryType = objectDicts[dictionaryTypeLocation[index]]
                if item not in dictionaryType:
                    newLinkedItem = linkedObject(item)
                    dictionaryType[item] = newLinkedItem
                if lastItemFound:
                    dictionaryType[item].addLink(lastItemFound)
                lastItemFound = dictionaryType[item]
            # # Uneeded, but we can relate these other items anyways for future use.
            # else:
                # newLinkedItem = linkedObject(item)
                # if lastItemFound:
                    # newLinkedItem.addLink(lastItemFound)
                # lastItemFound = newLinkedItem

## Clean all phone numbers given a list of column headers and a list of rows. Any column that matches phone will be
#  cleaned to a 10 digit string standard or '' if the format is invalid.
#  @param objectList The list of rows of csv data.
#  @param objectTypes The list of column headers (types) of csv data.
def cleanAllPhoneNumbers(objectList, objectTypes):
    phoneNumberTypeRegex = "[pP]hone"
    phoneColumns = [offset  for offset, type in enumerate(objectTypes) if re.search(phoneNumberTypeRegex, type)]
    for row in objectList:
        for offset in phoneColumns:
            row[offset] = cleanPhoneNumber(row[offset])

## Clean a phone number as a string into a standard 10 digit format.
#  @param number The phone number as a string.
#  @return The number as a 10 digit string or '' if the format is incorrect.
def cleanPhoneNumber(number):
        match = re.match("1?.*(\d{3}).*(\d{3}).*(\d{4})",number)
        if match:
            return "".join(match.group(1,2,3))
        else:
            return ''

## Turns a list of strings into a csv string.
#  @param list The list of strings.
#  @return A string of , seperated strings with a newline at the end.
def listToCSV(list):
    return ",".join(list) + "\n"

## Assign Ids in number order to the linked Object lists and return the last Id not assigned.
#  @param objectDicts The list of dictionaries for the matching types.
#  @return The last unassigned ID.
def assignUniqueIds(objectDicts):
    id = 0
    for index, dictType in enumerate(objectDicts):
        for item in dictType:
            linkedItem = dictType[item]
            IdAssigned = False
            for element in linkedItem:
                element.itemID = id
                IdAssigned = True
            if IdAssigned:
                id += 1
    return id
    

###########################
# Main script for parsing the csv file and writing the solution out. 
def main():
    if  len(sys.argv) == 1:
        print """Usage: python vectorizer.py <input csv> <regex1> <regex2>
                  Where regex is the types to match on.                     """
        exit()

    with open(sys.argv[1],"rU") as fdCSVReader:
        objectTypes = parseHeader(fdCSVReader)
        objectList = parseLines(fdCSVReader)
        
    colsToMatchOn = []
    defaultTypesRegex = ["[pP]hone", "[eE]mail"]
    typeRegexes = defaultTypesRegex
    
    # Read in extra args as regex to match types.
    if len(sys.argv) > 2:
        typeRegexes = sys.argv[2:]

    # Create a dictionary for each type
    objectDicts = [{} for x in typeRegexes]
    dictionaryTypeLocation = []
    
    # Create a mapping of column to dictionary (place like types together).
    for type in objectTypes:
        for dictOffset, typeRegex in enumerate(typeRegexes):
            # If there is a type store its dict's index else mark it as None.
            if re.search(typeRegex, type):
                dictionaryTypeLocation.append(dictOffset)
                break
        else:
            dictionaryTypeLocation.append(None)

    cleanAllPhoneNumbers(objectList, objectTypes)
    populateDicts(objectList, objectDicts, dictionaryTypeLocation)
    id = assignUniqueIds(objectDicts)

    # Write out the output file
    with open("Out.txt","w") as fdWriter:
        for list in objectList:
            for index, item in enumerate(list):
                if item and dictionaryTypeLocation[index] != None:
                    fdWriter.write( "id is :" + str(objectDicts[dictionaryTypeLocation[index]][item].itemID) + " ")
                    fdWriter.write( listToCSV(list))
                    break;
            else:
                fdWriter.write("id is :" + str(id) + " " + listToCSV(list))
                id += 1
###########################

main()