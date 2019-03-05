# Improve rendering
Changing a model may be a really long process. This can be partially
solved using add-on (802285486)[https://ankiweb.net/shared/info/802285486] (full disclosure: I also wrote it). As an
example, I've got a note type with more than a hundred field and card
type. Changing it without this add-on takes 7 minutes and a half while
using this add-on, it takes only 3 minutes.

## Warning
This change the result of the card generated in a few case. Most of
them should either be improvement, or not occur in normal use of anki.

### Field name inside field.
In a basic card, if you write "{{Back}}" in the Front field, you'll
see the content of the back field where you should see the front
field. This is because {{Back}} is found in the generated card and
anki assumes it must be replaced by the value of the Back field.


### More than a hundred field.
By default, anki allows at most a hundred field by card. This add-on
remove this restriction. Thanks to the time improvement, this is
actually not an important limit anymore.

### Badly formed card type
A template such as
```
{{#Front}}{{#Back}} {{Front}}{{Back}}{{/Front}} {{/Back}}
```
is theoretically invalid. Indeed, you should cloze Back before Front
since you opened it after Front. If you create a note with some value
in Back and no value in Front, you'll see the message "{unknown field
/Back}" (which is a really badly wrnitten error message). However,
anki will still generate some content when you use this model. It is possible that the content
generated with and without this add-on will differ. 

## Internal
This modify the following method, without calling the previous
version.

* anki.template.template.Template.render_sections
* anki.template.template.Template.render_tags

## Technical description
Anki generate a card content as follow. It search for the first
section (i.e. {{#foo}}bar{{/foo}} or {{^foo}}bar{{foo}}), and replace
it either by bar, or by the empty string. It does this until no such
replacement can be done. Then it search for the first tag
(i.e. {{foo}}), and when it is found, it replace all {{foo}} by the
value of the field foo. It does so at most a hundred time and halts
when there are no {{foo}} anymore.

The first process takes times proportional to the product of the
number of section times the size of the card type. The second process
takes time proportional to the product of the number of distinct field
and the size of the card type. 

This add-ons ensure anki does all replacement in a single pass,
instead of doing it iteratively. Thus the running time is the sum of
the length of the card type, of the number of sectiond and of the
number of tags.
