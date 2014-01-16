DICOMSearch
===========

A utility to put the DICOM standard into a searchable database with web app


This uses python to parse a local copy of the DocBook xml version of the standard (still 
in development and not publicly available).  The paragraphs are converted into couchdb
documents and pushed to the server.  Each word in the paragraph is also linked back
to the paragraph so that it is easy (quick) to search the standard by keyword
and get all matching instances.
