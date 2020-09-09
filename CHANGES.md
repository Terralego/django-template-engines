
CHANGELOG
=========

1.3.1           (2020-09-09)
----------------------------

* Support django 3.1


1.3.0           (2020-06-09)
----------------------------

* Implement Weasyprint PDF Template Engine


1.2.29          (2020-06-05)
----------------------------

* Verify if ODT or DOCX file are zippable file to avoid exceptions


1.2.28          (2020-04-14)
----------------------------

* Fix cases when image didn't fit page


1.2.27          (2020-04-14)
----------------------------

* Translate img tag in from_html for odt templates


1.2.26          (2020-05-04)
----------------------------

* Fix deprecation warnings and bad closing files


1.2.25          (2020-02-24)
----------------------------

* Fix span tags with text:span in from_html


1.2.24          (2019-12-02)
----------------------------

* Add rendering of footer and header


1.2.23          (2019-11-29)
----------------------------

* Remove automatically resize
* Change value conversion px to odt
* Add extension at the end of the generated file


1.2.22          (2019-11-25)
----------------------------

* Change AbstractEngine, inheritate from DjangoTemplates

1.2.21          (2019-11-18)
----------------------------

* Fix context rendering odt.

1.2.20          (2019-11-15)
----------------------------

* fix max_height and max_width


1.2.19          (2019-11-14)
----------------------------

* Add anchor image_url_load, image_load
* Replace width and height for image_url_load, image_load by max_width and max_height


1.2.18          (2019-11-13)
----------------------------

* fix odt image inclusion


1.2.17          (2019-11-07)
----------------------------

* Load odt_tags and docx_tags automatically, remove loads to make it works
* Add tag image_url_load
* Fix odt pictures inside zip


1.2.16          (2019-11-04)
----------------------------

* Allow heading, and text-numbered list in from_html odt tag


1.2.15          (2019-10-28)
----------------------------

* Fix text-input replacement for list inside paragraphs


1.2.14          (2019-10-25)
----------------------------

* Fix text-input replacement for odt
* Add custom style for italic and underline text for html filter


1.2.13      (2019-10-25)
------------------------

Features:

* from_html tag filter for odt templates


1.2.12      (2019-10-23)
------------------------

Fixes:

* automatic escape break line in odt template


1.2.11      (2019-10-23)
------------------------

Improve:

* automatic escape break line in odt template


1.2.10      (2019-10-09)
------------------------

Improve:

* Tags are renamed
* ODT image inclusion


Update:
 * From now on, ``{% ... %}`` are also cleaned.

1.2.9       (2019-09-24)
------------------------

Other:
 * the template is cleaned before it is filled.

1.2.8       (2019-09-24)
------------------------

Optimize:
 * clean methods

Add:
 * a method that removes incorrect additions in the template tags of the xml file

Update:
 * the documentation

Fix:
 * requirements

Other:
 * ``AbstractEngine`` becomes ``ZipAbstractEngine`` and allow you to write
   custom engines for zip base documents

1.2.7       (2019-09-12)
------------------------

Fixes:
 * template generation from different django storage

1.2.6       (2019-09-12)
------------------------

Fixes:
 * conditions to determine mimetype template


1.2.5       (2019-09-12)
------------------------

Fixes:
 * packaging
 

1.2.4       (2019-09-12)
------------------------

Fixes:
 * Allow mimetype zip for DOCX and ODT

1.2.3       (2019-09-11)
------------------------

Fixes:
 * Compatibility with non FileStorageBackend

1.2.2
-----

Update
* Pillow>=5.4.1

1.2.1
-----

`requests` is no longer needed.

1.2.0
-----

From now on, you can specify bold text.

1.1.3
-----
Image loaders can now take width and height as `dxa`, `px`, `pt`, `in`, `cm`
and `emu`.

1.1.2
-----

Add:

* A template tag to load images into a docx template (`docx_image_loader`).

1.0.0
-----

Add:

* Docx template engine (`template_engines.backends.docx.DocxEngine`).
* Docx template class (`template_engines.backends.odt.DocxTemplate`).

0.0.4
-----

* Abstract template engine for writing custom engines
  (`template_engines.backends.abstract.AbstractEngine`).
* Abstract template class for writing custom template classes
  (`template_engines.backends.abstract.AbstractTemplate`).
* Odt template engine (`template_engines.backends.odt.OdtEngine`).
* Odt template class (`template_engines.backends.odt.OdtTemplate`).
* A template tag to load images into an odt template (`odt_image_loader`).
