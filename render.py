from anki.template.template import Template, get_or_attr, modifiers
from anki.utils import stripHTMLMedia
import re

def render_sections(self, template, context):
    """replace {{#foo}}bar{{/foo}} and {{^foo}}bar{{/foo}} by
    their normal value."""
    n = 1
    def sub_section(match):
        section, section_name, inner = match.group(0, 1, 2)
        section_name = section_name.strip()
    
        # val will contain the content of the field considered
        # right now
        val = None
        m = re.match("c[qa]:(\d+):(.+)", section_name)
        if m:
            # get full field text
            txt = get_or_attr(context, m.group(2), None)
            m = re.search(clozeReg%m.group(1), txt)
            if m:
                val = m.group(1)
        else:
            val = get_or_attr(context, section_name, None)
        replacer = ''
        # Whether it's {{^
        inverted = section[2] == "^"
        # Ensuring we don't consider whitespace in wval
        if val:
            val = stripHTMLMedia(val).strip()
        if (val and not inverted) or (not val and inverted):
            replacer = inner
            
        return replacer
    while n:
        template, n = self.section_re.subn(sub_section, template)
    return template

Template.render_sections = render_sections


def render_tags(self, template, context):
    """Renders all the tags in a template for a context. Normally
    {{# and {{^ are already removed."""
    def sub_tag(match):
        tag, tag_type, tag_name = match.group(0, 1, 2)
        # i.e. "{{!foo}}", "!", "foo"
        tag_name = tag_name.strip()
        func = modifiers[tag_type]
        replacement = func(self, tag_name, context)
        return replacement
    try:
        return self.tag_re.sub(sub_tag,template)
    except (SyntaxError, KeyError):
        return "{{invalid template}}"



Template.render_tags = render_tags
