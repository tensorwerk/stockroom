from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# init console object to be used throught.
console = Console()


def print_columns_added(splits_added: dict):
    """
    Builds a Rich Table with the infor about the new columns created.

    Parameters
    ----------
    splits_added : dict containing the column_names and length of each split

    Returns
    -------
    Table
        The final generated table ready to be displayed

    """
    table = Table(box=box.MINIMAL)

    table.add_column("Split [len]", no_wrap=True, justify="right", style="bold green")
    table.add_column("Column Names")

    for split in splits_added:
        column_names, num_samples = splits_added[split]
        table.add_row(split + f" [{num_samples}]", ", ".join(column_names))

    console.print(table)


def print_experiment_tags(tags: dict):
    """
    Builds and prints Rich table with tags and values
    """
    table = Table(box=box.MINIMAL)

    table.add_column("Tags", style="medium_orchid")
    table.add_column("Values", justify="right")

    for tag in tags:
        table.add_row(tag, str(tags[tag]))

    console.print(table)


def print_data_summary(column_info: list):
    """
    Builds and prints Rich table with tags and values
    """
    table = Table(box=box.SQUARE)

    table.add_column("Column Name", style="medium_orchid")
    table.add_column("Number of samples", justify="right")
    table.add_column("shape", justify="right")
    table.add_column("dtype", justify="right")

    for col in column_info:
        name, length, shape, dtype = col
        table.add_row(name, str(length), str(shape), str(dtype))

    console.print(table)


def print_models_table(models: tuple):
    """
    Builds and prints Rich table with the models in the stock repo
    """
    table = Table(box=box.SIMPLE_HEAVY)

    table.add_column("Models", style="medium_orchid")

    for model in models:
        table.add_row(model)

    console.print(table)


def print_current_head(head: str):
    """
    Prints the current head
    """
    text = Text(justify="left")
    text.append("Current Head: ")
    text.append(head[2:9], style="medium_orchid")
    head_panel = Panel(text, box=box.MINIMAL)

    console.print(head_panel)
