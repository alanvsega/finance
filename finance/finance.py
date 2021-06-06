import click


@click.command()
@click.option('--count', default=1, help='Number of greetings.')
def finance(count, name):


if __name__ == '__main__':
    finance()