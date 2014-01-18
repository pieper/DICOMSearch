DICOMSearch
===========

A utility to put the DICOM standard into a searchable database with web app

This uses python to parse a local copy of the DocBook xml version of the standard (still
in development and not publicly available).  The paragraphs are converted into couchdb
documents and pushed to the server.  Each word in the paragraph is also linked back
to the paragraph so that it is easy (quick) to search the standard by keyword
and get all matching instances.

A utility couchSite copies the local site directory as attachments to a document
called .site so that the site can be hosted directly from CouchDB.  The site
allows you to type a keyword and get instant results.

You can search by passing commands with the URL like this:

http://127.0.0.1:5984/dicom_search/.site/index.html?search=orientation

http://127.0.0.1:5984/dicom_search/.site/index.html?search=(0008,0008)


Caveats
=======

This is very much a quick and dirty prototype as a practice to get comfortable
with the standard and play with couchdb as a web app back end.

Some things that this doesn't support:

- searches for words less than 5 letters long

- multi-word searches

- boolean operations or wildcards

- linking into a full version of the standard

- figures, tables, and other items from the standard

- a DICOM data dictionary for quick lookup
