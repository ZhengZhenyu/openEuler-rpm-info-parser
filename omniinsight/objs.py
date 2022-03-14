import os
import yaml


class ProjectData:
    def __init__(self, name, sig):
        self.name = name
        self.sig = sig


class RpmData:
    def __init__(self, name):
        self.name = name
        self.id = ''
        self.short_name = ''
        self.arch = ''
        self.group = ''
        self.description = ''
        self.requires = []
        self.provides = []
        self.oe_release = ''
        self.sig = ''
        self.project = ''

    def to_dict(self):
        rpm_dict = {
            'name': self.name,
            'short_name': self.short_name,
            'arch': self.arch,
            'group': self.group,
            'description': self.description,
            'requires': self.requires,
            'provides': self.provides,
            'oe_release': self.oe_release,
            'sig': self.sig,
            'project': self.project
        }

        return rpm_dict


class SigData:
    def __init__(self, name):
        self.name = name
        self.mentors = []
        self.maintainers = []
        self.committers = []
        self.description = ''

    def to_dict(self):
        sig_dict = {
            'name': self.name,
            'mentors': self.mentors,
            'maintainers': self.maintainers,
            'committers': self.committers,
            'description': self.description
        }
        return sig_dict

    def parse_sig_yaml(self, file_path):
        with open(file_path, 'r') as sig_yaml:
            yaml_data = yaml.load(sig_yaml, Loader=yaml.SafeLoader)

            self.description = yaml_data.get('description')
            self.mentors = yaml_data.get('mentors')
            self.maintainers = yaml_data.get('maintainers')
            self.committers = yaml_data.get('committers')
