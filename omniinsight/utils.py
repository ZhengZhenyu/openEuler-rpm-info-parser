import json
import os
import shutil
import subprocess
import sys
import yaml


def parse_yaml_list(list_file, keyword):
    if not list_file:
        raise Exception

    with open(list_file, 'r') as inputs:
        input_dict = json.load(inputs)

    return input_dict[keyword]


def clean_up_dir(target_dir):
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)


def prepare_workspace(config_options):
    work_dir = config_options['working_dir']
    clean_up_dir(work_dir)
    os.makedirs(work_dir)

    verbose = False
    if config_options.get('debug'):
        verbose = True

    return work_dir, verbose


def clone_source(src_url, dest_dir, pkg_name, branch=None):
    print('Fetching: ' + pkg_name + ' ...')
    orig_dir = os.getcwd()
    os.chdir(dest_dir)
    cmd = 'git clone '
    if branch:
        cmd = cmd + '-b ' + branch + ' '
    cmd = cmd + src_url
    subprocess.run(cmd, shell=True)
    os.chdir(orig_dir)

    return dest_dir + '/' + pkg_name


def check_option(option, keyword):
    if not option:
        print('Should provide a valid %s!' % keyword)
        sys.exit(1)


def check_and_load_config(config_file):
    check_option(config_file, 'config file')

    with open(config_file, 'r') as config_file:
        config_options = yaml.load(config_file, Loader=yaml.SafeLoader)

    return config_options
