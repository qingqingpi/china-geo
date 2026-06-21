"""DomScanner 畸形 / 边界 HTML 加固——一遍 html.parser 扫信号，零依赖替代 BeautifulSoup。

补 test_dom.py 的盲区：HTML 注释、实体解码、大小写标签、script/style 内含标签、
未闭合标签、meta property、img alt 三态、scan("")/scan(None)/超大输入。
均为对当前行为的 characterization（绿）。
"""
from seogeo.dom import scan


# ---- HTML 注释：html.parser 把注释内容剥离，不计入文本 / 标题 ----

def test_comment_content_not_counted_as_headings():
    # 注释里的 <h1> 是假标题，不该被当成真标题计数
    d = scan("<p>真实<!-- 注释里有 <h1>假标题</h1> -->内容</p>")
    assert d.headings["h1"] == 0


def test_comment_stripped_from_visible_text():
    d = scan("<p>真实<!-- 注释 -->内容</p>")
    assert d.text == "真实内容"
    assert d.paragraph_lengths == [4]  # 真+实+内+容


# ---- 实体解码（convert_charrefs=True）----

def test_entities_decoded_in_title():
    assert scan("<title>A&amp;B</title>").title == "A&B"


def test_entities_decoded_in_text_and_counted():
    d = scan("<p>&lt;tag&gt;</p>")  # → <tag>，5 个可见字符
    assert d.text == "<tag>"
    assert d.text_length == 5


# ---- 大小写标签 / 属性（HTMLParser 归一化为小写）----

def test_uppercase_tags_and_attrs_recognized():
    d = scan('<HTML LANG="zh-CN"><TITLE>标题</TITLE><H1>X</H1><H2>Y</H2></HTML>')
    assert d.lang == "zh-CN"
    assert d.title == "标题"
    assert d.headings["h1"] == 1
    assert d.headings["h2"] == 1


def test_jsonld_type_attr_case_insensitive():
    # type="APPLICATION/LD+JSON" 仍应被识别为 JSON-LD 块
    d = scan('<script type="APPLICATION/LD+JSON">{"@type":"X"}</script>')
    assert len(d.jsonld_blocks) == 1


# ---- script/style 内含"看似标签"的内容不破坏解析 ----

def test_script_with_anglebrackets_does_not_leak_or_break_capture():
    # 脚本里出现 </p> 文本不应中断段落捕获、也不计入可见文本
    d = scan('<script>if (a<b) { x="</p>"; }</script><p>真</p>')
    assert "x=" not in d.text
    assert d.text == "真"
    assert d.paragraph_lengths == [1]


def test_style_content_excluded_from_text():
    d = scan("<style>.a{content:'</h1>'}</style><h1>真标题</h1>")
    assert "content" not in d.text
    assert d.headings["h1"] == 1


# ---- meta：name 与 property 都收，property 落 metas ----

def test_meta_property_and_name_both_collected():
    d = scan('<meta property="og:title" content="OG"><meta name="description" content="D">')
    assert d.metas["og:title"] == "OG"
    assert d.metas["description"] == "D"


# ---- 链接收集 ----

def test_collects_anchor_hrefs():
    d = scan('<a href="/a">x</a><a href="https://x.com/b">y</a><a>无href</a>')
    assert d.links == ["/a", "https://x.com/b"]  # 无 href 的 <a> 不计


# ---- img alt 三态：缺 alt 计入 / alt="" 不计 / 有 alt 不计 ----

def test_img_alt_three_states_counted_correctly():
    d = scan('<img src=a><img src=b alt=""><img src=c alt="x">')
    assert d.images == 3
    assert d.images_missing_alt == 1  # 仅完全缺 alt 的那张计入


# ---- 未闭合块在 EOF 被冲洗（HTML5 常省略闭合）----

def test_unclosed_paragraph_at_eof_recorded():
    d = scan("<p>" + "正" * 30)  # 无 </p>，EOF 时 scan() 冲洗
    assert d.paragraph_lengths == [30]


def test_unclosed_heading_text_recorded_at_eof():
    d = scan("<h2>什么是 GEO？")  # 无 </h2>
    assert d.heading_texts == ["什么是GEO？"]  # 文本去空白后保留问号


# ---- 退化输入：空串 / None / 纯文本 / 超大 ----

def test_scan_empty_string_is_safe():
    d = scan("")
    assert d.text == "" and d.text_length == 0
    assert d.headings["h1"] == 0
    assert d.jsonld_blocks == []


def test_scan_none_is_safe():
    # scan(None) 内部 feed("") —— 不崩，全空
    d = scan(None)
    assert d.text == "" and d.text_length == 0


def test_scan_bare_text_no_tags():
    d = scan("就是一段没有标签的纯文本")
    assert d.text == "就是一段没有标签的纯文本"
    assert d.text_length == 12
    assert d.paragraph_lengths == []  # 没有 <p> 块


def test_scan_large_input_does_not_crash():
    # 5 万字 + 1000 段，确保状态机不爆栈、字数统计正确
    big = ("<p>" + "字" * 50 + "</p>") * 1000
    d = scan(big)
    assert len(d.paragraph_lengths) == 1000
    assert all(n == 50 for n in d.paragraph_lengths)
    assert d.text_length == 50 * 1000


def test_word_count_splits_on_whitespace_for_english():
    # word_count 仅供英文参考（按空格切）
    assert scan("<p>hello world foo</p>").word_count == 3


def test_multiple_jsonld_blocks_collected_in_order():
    html = ('<script type="application/ld+json">{"@type":"A"}</script>'
            '<script type="application/ld+json">{"@type":"B"}</script>')
    d = scan(html)
    assert len(d.jsonld_blocks) == 2
    assert "A" in d.jsonld_blocks[0] and "B" in d.jsonld_blocks[1]
