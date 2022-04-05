import re

REGEX = r"(\s*[\w\d\-_:]+(?:=(?:(?:\"[^\"]*\")|(?:[^\s]+\s+)))*)"
SPECIAL_TAGS = "input", "img", "source"


def get_body(text):
    text = re.sub(r"[\n\t✓]", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"'([^s])", r'"\1', text)
    text = text.replace(u'\xa0', ' ')
    result = re.search(rf"<body{REGEX}*>(.*)</body>", text)
    return result


def clean_text(text):
    text = re.sub(rf"</?(?:no)?br{REGEX}*/?>", "", text)
    tags = [
            ("<script", "</script>"),
            ("<style", "</style>"),
            ("<!--", "-->")]
    for tag in tags:
        while tag[0] in text:
            start = text.index(tag[0])
            end = text.index(tag[1]) + len(tag[1])
            if start > end:
                raise RuntimeError
            text = text[:start] + text[end:]
    return text


def is_special(opentag):
    tag = opentag.group(1)
    return tag in SPECIAL_TAGS or "/>" in opentag.group(0)


def is_closed(opentag, closetag):
    if closetag is None:
        return -1
    return opentag is None or opentag.start(0) > closetag.start(0)
