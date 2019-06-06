# Improve rendering
Changing a model may be a really long process. This can be partially
solved using add-on ()[] (full disclosure: I also wrote it). As an
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

This does not occur anymore. This add-ons ensure anki does all
replacement in a single pass, instead of doing it iteratively. On a
technical side, this is what allow the running time to be linear in
the number of field instance instead of quadratic (product of length
and of number of distinct field).

### More than a hundred field.
By default, anki allows at most a hundred field by card. This add-on
remove this restriction. Thanks to the time improvement, this is
actually not an important limit anymore.

### Badly formed card type
A template such as
```python
{{#Front}}{{#Back}} {{Front}}{{Back}}{{/Front}} {{/Back}}
```
is theoretically invalid. Indeed, you should cloze Back before Front
since you opened it after Front. If you create a note with some value
in Back and no value in Front, you'll see the message "{unknown field
/Back}" (which is a really badly written error message). However,
anki will still generate some content when you use this model. It is possible that the content
generated with and without this add-on will differ.

## Internal
This modify the following method, without calling the previous
version.

* anki.template.template.Template.render_sections
* anki.template.template.Template.render_tags
It also creates the methods:
* anki.template.template.Template.sub_section
* anki.template.template.Template.sub_tag

## Links, licence and credits

Key         |Value
------------|-------------------------------------------------------------------
Copyright   | Arthur Milchior <arthur@milchior.fr>
Based on    | Anki code by Damien Elmes <anki@ichi2.net>
License     | GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
Source in   | https://github.com/Arthur-Milchior/anki-better-card-generation
Addon number| [115825506](https://ankiweb.net/shared/info/115825506)
Support me on| [![Ko-fi](https://ko-fi.com/img/Kofi_Logo_Blue.svg)](Ko-fi.com/arthurmilchior) or [![Patreon](http://www.milchior.fr/patreon.png)](https://www.patreon.com/bePatron?u=146206)
