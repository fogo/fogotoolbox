# -*- coding: utf8 -*-

from fogotoolbox.markdown.table_contents import md_table_contents

filler = """\
whatever
* something
```
code?
```
"""


def test_empty():
    assert md_table_contents(md="") == ""


def test_simple():
    md = """\
# One

{filler}

## Two

{filler}

### Three

{filler}

#### Four

{filler}

""".format(filler=filler)

    assert md_table_contents(md=md) == """\
* [One](#one)
  * [Two](#two)
    * [Three](#three)
      * [Four](#four)"""


def test_replacing_forbidden():
    md = """\
# (parentheses)

{filler}

### Colon: yes

{filler}

## "Quoted"

{filler}

#### Comma, why not

{filler}

### Question mark?

{filler}

## Hyphen - or else

{filler}

### ... dots

{filler}

### привет welcome to unicode

{filler}
""".format(filler=filler)

    assert md_table_contents(md=md) == """\
* [(parentheses)](#parentheses)
    * [Colon: yes](#colon-yes)
  * ["Quoted"](#quoted)
      * [Comma, why not](#comma-why-not)
    * [Question mark?](#question-mark)
  * [Hyphen - or else](#hyphen-or-else)
    * [... dots](#dots)
    * [привет welcome to unicode](#привет-welcome-to-unicode)"""
