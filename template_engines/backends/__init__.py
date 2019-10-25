import re


TO_CHANGE_RE = re.compile(r'\n|&lt;b&gt;|&lt;/b&gt;')

DOCX_PARAGRAPH_RE = re.compile(
    r'<w:r><w:rPr>([^>]*)</w:rPr><w:t>[^<]+</w:t></w:r\>')
DOCX_CHANGES = {
    '\n': '</w:t><w:br/><w:t>',
    '&lt;b&gt;': '</w:t></w:r><w:r><w:rPr>{}<w:b w:val="true"/></w:rPr><w:t>&#xA0;',
    '&lt;/b&gt;': '&#xA0;</w:t></w:r><w:r><w:rPr>{}<w:b w:val="false"/></w:rPr><w:t>',
}
