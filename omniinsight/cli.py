import click
from flask import Flask
import prettytable as pt

import omniinsight.insight as insight
import omniinsight.utils as utils


app = Flask(__name__)


@click.command()
@click.argument('resource_type')
@click.option('--config-file', help='Configuration file for the software')
def load(resource_type, config_file):
    config_options = utils.check_and_load_config(config_file)
    insight.do_load(resource_type, config_options)


@click.command()
@click.argument('resource_type')
@click.option('--config-file', help='Configuration file for the software')
@click.option('--release-name', help='Option for list rpms, specify the release that you want to query')
@click.option('--sig-name', help='Option for list rpms, specify the sig name that you want to query')
@click.option('--arch', help='Option for list rpms, specify the arch name that you want to query,'
                             'the available values are [x86_64, aarch64, all]')
def list(resource_type, config_file, release_name, sig_name, arch):
    config_options = utils.check_and_load_config(config_file)

    ret = insight.do_list(resource_type, config_options, release_name, sig_name, arch)
    tb = pt.PrettyTable()

    if resource_type == 'rpms':

        tb.field_names = ["Package Name", "SIG", "Release", "Arch"]

        for rpm in ret:
            tb.add_row([rpm.name, rpm.sig, rpm.oe_release, rpm.arch])

        print(tb)

    elif resource_type == 'sigs':

        tb.field_names = ["SIG Name", "Description", "Mentors", "Maintainers", "Committers"]

        for sig in ret:
            tb.add_row([sig.name, sig.description, sig.mentors, sig.maintainers, sig.committers])

        print(tb)


@click.command()
@click.argument('resource_type')
@click.argument('resource_id')
@click.option('--config-file', help='Configuration file for the software')
def get(resource_type, resource_id, config_file):
    config_options = utils.check_and_load_config(config_file)
    ret = insight.do_get(resource_type, resource_id, config_options)
    tb = pt.PrettyTable()

    if resource_type == 'sig':
        tb.field_names = ["SIG Name", "Description", "Mentors", "Maintainers", "Committers"]

        tb.add_row([ret.name, ret.description, ret.mentors, ret.maintainers, ret.committers])

        print(tb)

    elif resource_type == 'rpm':
        tb.field_names = ["Package Name", "SIG", "Release", "Package Group", "Requires", "Provides", "Arch"]

        for rpm in ret:
            tb.add_row([rpm.name, rpm.sig, rpm.oe_release, rpm.group, rpm.requires, rpm.provides, rpm.arch])

        print(tb)


@click.group()
def cli():
    pass


if __name__ == '__main__':
    cli.add_command(load)
    cli.add_command(list)
    cli.add_command(get)
    cli()
