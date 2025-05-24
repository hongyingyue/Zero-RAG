from typer import Typer

from cli.codegen import codegen
from cli.erd_gen import erd_gen
from cli.gqlgen import gqlgen
from cli.perm_gen import perm_gen
from cli.print_config import print_config
from cli.sanity_check import sanity_check

cli = Typer()

cli.command("codegen")(codegen)
cli.command("print-config")(print_config)
cli.command("sanity-check")(sanity_check)
cli.command("gqlgen")(gqlgen)
cli.command("perm_gen")(perm_gen)
cli.command("erd_gen")(erd_gen)
