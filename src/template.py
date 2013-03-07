import os

HEADER = """
======================================================================
Report
  Generated at {date}
  On {server}
======================================================================

"""

FOOTER = """
---- END OF REPORT ----
"""

OUTER = """

----------------------------------------------------------------------
{filename} contains {item_count} errors:
----------------------------------------------------------------------
"""

LINE_ITEM = """
  {when}
  {who}
  {message}
  {extra}
"""

def generate_header(date, server="localhost"):
    generated = date.isoformat()
    return HEADER.format(**locals())

def generate_footer():
    return FOOTER

def generate_block(logfile, items):
    item_count = len(items)
    filename = os.path.basename(logfile)

    block = OUTER.format(**locals())

    for item in items:
        block = "\n".join([block, LINE_ITEM.format(**item)])

    return block