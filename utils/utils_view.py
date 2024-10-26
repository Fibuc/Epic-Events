from rich.console import Console
from rich.table import Table
from rich.theme import Theme

COLORS = ['green', 'cyan', 'blue', 'magenta', 'dark_green', 'bright_blue', 'yellow', 'white', 'black']

def get_console(theme=None):
    return Console(theme=theme)


def get_success_error_console():
    theme = Theme({'success': 'green', 'error': 'bold red'})
    return get_console(theme)


def get_table(title: str, column_names: list[str]):
    table = Table(title=title)
    for i, name in enumerate(column_names):
        if name in ['Numéro', 'ID', 'Montant total', 'Déjà réglé', 'N°Contrat', 'Restant dû']:
            table.add_column(name, style=COLORS[i], justify='right')
        else:
            table.add_column(name, style=COLORS[i])

    return table


def convert_date(datetime_obj):
    return datetime_obj.strftime('Le %d/%m/%Y à %H:%M')


def space():
    console = get_console()
    console.print()
    console.print()