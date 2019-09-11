# Versions


## 1.2.2    (2019-09-11)

Fixes:
 * Compatibility with non FileStorageBackend

## 1.2.2

`Pillow>=5.4.1`

## 1.2.1

`requests` is no longer needed.

## 1.2.0

From now on, you can specify bold text.

## 1.1.3

Image loaders can now take width and height as `dxa`, `px`, `pt`, `in`, `cm`
and `emu`.

## 1.1.2

Add:

* A template tag to load images into a docx template (`docx_image_loader`).

## 1.0.0

Add:

* Docx template engine (`template_engines.backends.docx.DocxEngine`).
* Docx template class (`template_engines.backends.odt.DocxTemplate`).

## 0.0.4

* Abstract template engine for writing custom engines
  (`template_engines.backends.abstract.AbstractEngine`).
* Abstract template class for writing custom template classes
  (`template_engines.backends.abstract.AbstractTemplate`).
* Odt template engine (`template_engines.backends.odt.OdtEngine`).
* Odt template class (`template_engines.backends.odt.OdtTemplate`).
* A template tag to load images into an odt template (`odt_image_loader`).
