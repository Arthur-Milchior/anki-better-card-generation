# from anki.template.template import Template
import time
import anki
from anki.models import ModelManager
from anki.sound import stripSounds
from anki.utils import splitFields
from anki.consts import *
import re
from anki.hooks import  runFilter

# oldRender = Template.render
# def render(*args,**kwargs):
#     start = time.clock()
#     end = time.clock()
#     ret = oldRender(*args,**kwargs)
#     dif = end-start
#     print(f"Render took {dif} seconds")
#     return ret

# Template.render = render

from anki.collection import _Collection

old_updateRequired = ModelManager._updateRequired
def _updateRequired(*args,**kwargs):
    start = time.clock()
    ret = old_updateRequired(*args,**kwargs)
    end = time.clock()
    dif = end-start
    print(f"_updateRequired took {dif} seconds")
    return ret
ModelManager._updateRequired = _updateRequired

def renderQA(self, ids=None, type="card"):
    # gather metadata
    """TODO

    The list of renderQA for each cards whose type belongs to ids.

    Types may be card(default), note, model or all (in this case, ids is not used).
    It seems to be called nowhere
    """
    if type == "card":
        where = "and c.id in " + ids2str(ids)
    elif type == "note":
        where = "and f.id in " + ids2str(ids)
    elif type == "model":
        where = "and m.id in " + ids2str(ids)
    elif type == "all":
        where = ""
    else:
        raise Exception()
    start = time.clock()
    t= [self._renderQA(row)
            for row in self._qaData(where)]
    end = time.clock()
    dif = end-start
    print(f"Renders took {dif} seconds")
    return t
#_Collection.renderQA = renderQA
    
def _renderQA(self, data, qfmt=None, afmt=None):
    """Returns hash of id, question, answer.

    Keyword arguments:
    data -- [cid, nid, mid, did, ord, tags, flds] (see db
    documentation for more information about those values)
    This corresponds to the information you can obtain in templates, using {{Tags}}, {{Type}}, etc..
    qfmt -- question format string (as in template)
    afmt -- answer format string (as in template)

    unpack fields and create dict
    TODO comment better

    """
    cid, nid, mid, did, ord, tags, flds, cardFlags = data
    flist = splitFields(flds)#the list of fields
    fields = {} #
    #name -> ord for each field, tags
    # Type: the name of the model,
    # Deck, Subdeck: their name
    # Card: the template name
    # cn: 1 for n being the ord+1
    # FrontSide :
    model = self.models.get(mid)
    for (name, (idx, conf)) in list(self.models.fieldMap(model).items()):#conf is not used
        fields[name] = flist[idx]
    fields['Tags'] = tags.strip()
    fields['Type'] = model['name']
    fields['Deck'] = self.decks.name(did)
    fields['Subdeck'] = fields['Deck'].split('::')[-1]
    if model['type'] == MODEL_STD:#Note that model['type'] has not the same meaning as fields['Type']
        template = model['tmpls'][ord]
    else:#for cloze deletions
        template = model['tmpls'][0]
    fields['Card'] = template['name']
    fields['c%d' % (ord+1)] = "1"
    # render q & a
    d = dict(id=cid)
    # id: card id
    qfmt = qfmt or template['qfmt']
    afmt = afmt or template['afmt']
    start = time.clock()
    for (type, format) in (("q", qfmt), ("a", afmt)):
        if type == "q":
            format = re.sub("{{(?!type:)(.*?)cloze:", r"{{\1cq-%d:" % (ord+1), format)
            #Replace {{'foo'cloze: by {{'foo'cq-(ord+1), where 'foo' does not begins with "type:"
            format = format.replace("<%cloze:", "<%%cq:%d:" % (
                ord+1))
            #Replace <%cloze: by <%%cq:(ord+1)
        else:
            format = re.sub("{{(.*?)cloze:", r"{{\1ca-%d:" % (ord+1), format)
            #Replace {{'foo'cloze: by {{'foo'ca-(ord+1)
            format = format.replace("<%cloze:", "<%%ca:%d:" % (
                ord+1))
            #Replace <%cloze: by <%%ca:(ord+1)
            fields['FrontSide'] = stripSounds(d['q'])
            #d['q'] is defined during loop's first iteration
        fields = runFilter("mungeFields", fields, model, data, self) # TODO check
        html = anki.template.render(format, fields) #replace everything of the form {{ by its value TODO check
        d[type] = runFilter(
            "mungeQA", html, type, fields, model, data, self) # TODO check
        # empty cloze?
        if type == 'q' and model['type'] == MODEL_CLOZE:
            if not self.models._availClozeOrds(model, flds, False):
                d['q'] += ("<p>" + _(
            "Please edit this note and add some cloze deletions. (%s)") % (
            "<a href=%s#cloze>%s</a>" % (HELP_SITE, _("help"))))
                #in the case where there is a cloze note type
                #without {{cn in fields indicated by
                #{{cloze:fieldName; an error message should be
                #shown
    end = time.clock()
    dif = end-start
    print(f"Renders took {dif} seconds")
    return d
#_Collection._renderQA = _renderQA
