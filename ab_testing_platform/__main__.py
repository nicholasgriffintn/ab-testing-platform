import click

from .lib.utils import load_user_data, parse_group_buckets
from .pipeline import run_experiment


@click.group()
def cli():
    """
    pipeline commands
    """


@cli.group()
def ab_testing():
    """
    AB Testing commands
    """


@click.command()
@click.option(
    "--group_buckets",
    required=True,
    type=str,
    help="Group buckets in the format 'group1:start-end,group2:start-end' (e.g., 'control:0-50,test1:50-100')",
    default="control:0-50,test1:50-100",
)
def input_data_manually(group_buckets):
    """
    Input user data manually and run an A/B test.
    """
    user_data = []
    while True:
        user_id = click.prompt("Enter User ID (or 'q' to quit)")
        if user_id == "q":
            break
        event = click.prompt(
            f"Did User {user_id} succeed? (1 for yes, 0 for no)", type=int
        )
        user_data.append({"user_id": user_id, "event": event})

    click.echo(f"Collected {len(user_data)} users. Now running the experiment.")
    group_buckets_dict = parse_group_buckets(group_buckets)
    click.echo(f"Using group buckets: {group_buckets_dict}")
    run_experiment(user_data, group_buckets_dict)


ab_testing.add_command(input_data_manually)


@click.command()
@click.option(
    "--file_path",
    required=True,
    type=click.Path(exists=True),
    help="The path to the JSON file containing user data",
    default="./tests/fixtures/ab-testing-users.json",
)
@click.option(
    "--group_buckets",
    required=True,
    type=str,
    help="Group buckets in the format 'group1:start-end,group2:start-end' (e.g., 'control:0-50,test1:50-100')",
    default="control:0-50,test1:50-100",
)
def load_data_from_file(file_path: str, group_buckets: str):
    """
    Load user data from a JSON file and run an A/B test.
    """
    try:
        user_data = load_user_data(file_path)
        click.echo(
            f"Loaded {len(user_data)} users from {file_path}. Now running the experiment."
        )
        group_buckets_dict = parse_group_buckets(group_buckets)
        click.echo(f"Using group buckets: {group_buckets_dict}")
        run_experiment(user_data, group_buckets_dict)
    except Exception as e:
        click.echo(f"Error loading file: {e}", err=True)


ab_testing.add_command(load_data_from_file)


if __name__ == "__main__":
    cli()