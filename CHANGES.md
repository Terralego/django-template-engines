## CHANGELOG

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
