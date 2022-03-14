import os
import yaml

import omniinsight.objs as objs


def get_file_path(root_path, file_list, dir_list):
    dir_or_files = os.listdir(root_path)
    for dir_file in dir_or_files:
        dir_file_path = os.path.join(root_path, dir_file)
        if os.path.isdir(dir_file_path):
            dir_list.append(dir_file_path)
            get_file_path(dir_file_path, file_list, dir_list)
        else:
            file_list.append(dir_file_path)


def parse_projects(root_path):
    projects = []
    file_list = []
    dir_list = []

    # Make a project_dict to quickly get project with corresponding sig
    project_dict = {}

    get_file_path(root_path, file_list, dir_list)

    for file in file_list:
        if not file.endswith('.yaml'):
            continue
        elif file.endswith('sig-info.yaml'):
            continue
        sig_name = file.split('/community/sig/')[1].split('/')[0]
        project_name = file.split('/omniinsight-openeuler/')[-1].split('/')[-1].split('.yaml')[0]
        project = objs.ProjectData(project_name, sig_name)

        project_dict[project_name] = sig_name

        projects.append(project)

    return projects, project_dict


def parse_sigs(root_path):
    sigs = []
    file_list = []
    dir_list = []

    get_file_path(root_path, file_list, dir_list)

    for file in file_list:
        if not (file.endswith('sig-info.yaml') or file.endswith('OWNERS')):
            continue
        sig_name = file.split('/community/sig/')[1].split('/')[0]
        sig = objs.SigData(sig_name)
        sig.parse_sig_yaml(file)

        sigs.append(sig)

    return sigs
