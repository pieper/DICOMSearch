#!/usr/bin/env python
"""
Create a CouchDB database with the contents of the DICOM Standard.

Add a view that maps all words to the section ids where they appear.

Use --help to see options.


TODO:
    Consider switching to elasticsearch or something similar
    https://github.com/elasticsearch/elasticsearch

    Maybe add DataTables for the output
    https://github.com/DataTables/DataTables
"""

import sys, os, traceback
import json, couchdb
import xml.etree.ElementTree as ET


# {{{ DICOMSearchParser
class DICOMSearchParser():
  """Parse xml files in the dicom standard and create the database.
  """
  

  def __init__(self,dicomStandardPath, couchDB_URL='http://localhost:5984', databaseName='dicom_search'):
    self.dicomStandardPath=dicomStandardPath
    self.couchDB_URL=couchDB_URL
    self.databaseName=databaseName

    self.ids = []
    self.paragraphNumber = 0

    self.nameMap = {
            'id' : '{http://www.w3.org/XML/1998/namespace}id',
            'para' : '{http://www.w3.org/XML/1998/namespace}para',
            }

    # create a fresh database
    self.couch = couchdb.Server(self.couchDB_URL)
    try:
        self.couch.delete(self.databaseName)
    except:
        pass
    self.db = self.couch.create(self.databaseName)

  def parseToDatabase(self):
    """Look through dicomStandardPath for xml files
    and then parse each one"""
    for root, dirs, files in os.walk(self.dicomStandardPath):
        for fileName in files:
            fileNamePath = os.path.join(root,fileName)
        try:
            if fileNamePath.endswith('.xml'):
                print("Parsing %s" % fileNamePath)
                self.parseDocBook(fileNamePath)
        except Exception, e:
            print ("Couldn't parse xml from %s" % fileNamePath)
            print str(e)
            traceback.print_exc()
            continue
  def save(self,jsonDictionary):
    try:
        self.db.save(jsonDictionary)
    except couchdb.ResourceConflict:
        print ("Could not save document")
        print (jsonDictionary)

  def loadDesign(self):
      """Load the design documents for the search views
      http://127.0.0.1:5984/dicom_search/_design/search/_view/paraByWord?key=%22acted%22&include_docs=true&reduce=false
      """
      self.db['_design/search'] = {
              'language' : 'javascript',
              'views' : {
                  'paraByWord' : {
                      'map' : '''
                        function(doc) {
                          if (doc.word) {
                            emit( doc.word, { "_id" : doc.paraID } );
                          }
                        }
                      ''',
                      'reduce' : '''_count()''',
                    }
                }
            }


  def parseDocBook(self,docBookPath):
    """Make a document for each para tag in the xml citing
    which section they are in.  Then make a document with each
    word in the paragraph pointing to that paragraph document id.
    """
    self.etree =ET.parse(docBookPath)
    part = self.etree.getroot()
    self.ids = [os.path.splitext(os.path.split(docBookPath)[-1])[0]]
    self.parseElement(part)

  def parseElement(self,element):
    if self.nameMap['id'] in element.attrib:
      self.ids.append(element.attrib[self.nameMap['id']])
      self.paragraphNumber = 1
    if element.tag == "{http://docbook.org/ns/docbook}para":
      jsonDictionary = {}
      paraID= ','.join(self.ids) + ',para_%d' % self.paragraphNumber
      jsonDictionary['_id'] = paraID
      jsonDictionary['text'] = element.text
      self.paragraphNumber += 1
      self.save(jsonDictionary)
      if element.text:
        try:
            words = set(map(str.lower, map(str,element.text.split())))
            for word in words:
                if len(word) > 4:
                    jsonDictionary = {}
                    jsonDictionary['_id'] = paraID + "," + word
                    jsonDictionary['paraID'] = paraID
                    jsonDictionary['word'] = word
                    self.save(jsonDictionary)
        except UnicodeEncodeError:
            print ("Could not handle unicode")
            print (element.text)

    for child in element:
        self.parseElement(child)
    if self.nameMap['id'] in element.attrib:
      self.ids.pop()


  def printElement(self,element, indent=0):
    """Print a single element (recursive)"""
    if self.skipSceneViews and element.tag == 'SceneView':
      return
    if element.tag in self.skipTags:
      return
    print(indent*' ' + '(')
    print(indent*' ' + element.tag)
    if self.idOnly:
      if 'id' in element.attrib:
        idString = element.attrib['id']
      else:
        idString = "noID"
      print(indent*' ' + idString)
      for key in element.attrib:
        if key.endswith('ID') or key.endswith('Ref'):
          print(indent*' ' + '...' + key + ': ' + element.attrib[key])
    else:
      print(indent*' ' + str(element.attrib))
    for child in element:
      self.printElement(child, indent=indent+4)
    print(indent*' ' + ')')

  def printScene(self):
    """Print the entire scene dom"""
    mrml = self.etree.getroot()
    self.printElement(mrml)

# }}}

# {{{ main, test, and arg parse

def usage():
    print ("DICOMSearch [DICOMStandard] <CouchDB_URL> <DatabaseName>")
    print (" CouchDB_URL default http:localhost:5984")
    print (" DatabaseName default DICOMSearch")

def main ():
    global parser
    dicomStandardPath = sys.argv[1]
    parser = DICOMSearchParser(dicomStandardPath)
    if len(sys.argv) > 2:
        parser.couchDB_URL = sys.argv[2]
    if len(sys.argv) > 3:
        parser.databaseName = sys.argv[3]

    parser.loadDesign()
    parser.parseToDatabase()

forIPython = """
import sys
sys.argv = ('test', '/Users/pieper/Downloads/dicom/DICOMStandard')
"""

if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            raise BaseException('missing arguments')
        main()
    except Exception, e:
        print ('ERROR, UNEXPECTED EXCEPTION')
        print str(e)
        traceback.print_exc()

# }}}

# vim:set sr et ts=4 sw=4 ft=python fenc=utf-8: // See Vim, :help 'modeline
# vim: foldmethod=marker
