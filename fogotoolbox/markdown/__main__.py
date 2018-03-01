import argparse
import io

from .table_contents import md_table_contents

parser = argparse.ArgumentParser(
    description="Generates table of contents for a markdown file based on "
                "its headers")
parser.add_argument(
    "md",
    metavar="MARKDOWN_FILE",
    nargs=1,
    type=str,
    help="Path to a Markdown file",
)
args = parser.parse_args()
md = args.md[0]

with io.open(md, "r", encoding="utf8") as f:
    print(md_table_contents(md=f.read()), file=None)
