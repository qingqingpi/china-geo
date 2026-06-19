"""DOM 扫描器：一遍 html.parser 扫出体检需要的全部信号，替代 BeautifulSoup（零依赖）。

中文要点：text_length 用"非空白字符数"，对中文（无空格）有效；word_count（按空格切）仅供英文参考。
"""
from seogeo.dom import scan


def test_extracts_title():
    d = scan("<html><head><title>你好 World</title></head></html>")
    assert d.title == "你好 World"


def test_counts_headings():
    d = scan("<h1>A</h1><h2>B</h2><h2>C</h2>")
    assert d.headings["h1"] == 1
    assert d.headings["h2"] == 2


def test_extracts_lang():
    d = scan('<html lang="zh-CN"></html>')
    assert d.lang == "zh-CN"


def test_extracts_canonical():
    d = scan('<link rel="canonical" href="https://x.com/a">')
    assert d.canonical == "https://x.com/a"


def test_extracts_meta_description():
    d = scan('<meta name="description" content="一段描述">')
    assert d.metas["description"] == "一段描述"


def test_collects_jsonld_blocks():
    d = scan('<script type="application/ld+json">{"@type":"Article"}</script>')
    assert len(d.jsonld_blocks) == 1
    assert "Article" in d.jsonld_blocks[0]


def test_skips_script_and_style_in_visible_text():
    d = scan("<p>真实内容</p><script>var x=1;</script><style>.a{color:red}</style>")
    assert "var x" not in d.text
    assert "color" not in d.text
    assert "真实内容" in d.text


def test_detects_lists_and_tables():
    d = scan("<ul><li>a</li></ul><table><tr><td>x</td></tr></table>")
    assert d.has_list is True
    assert d.has_table is True


def test_text_length_counts_chinese_chars():
    d = scan("<p>一二三四五</p>")
    assert d.text_length == 5  # 5 个汉字
