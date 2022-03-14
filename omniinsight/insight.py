from flask import Flask, request
import prettytable as pt
import sys


import omniinsight.db as db
import omniinsight.project_parser as project_parser
import omniinsight.rpm_parser as rpm_parser
import omniinsight.utils as utils


CONFIG_FILE = '/etc/omni-insight/conf.yaml'

config_options = utils.check_and_load_config(CONFIG_FILE)

app = Flask(__name__)


def do_load(resource_type, config_options):
    workdir, debug = utils.prepare_workspace(config_options)
    db.prepare_database(config_options, 'openEuler-rpms')

    # Clone openeuler/community repo and parse sig information
    COMMUNITY_URL = "https://gitee.com/openeuler/community.git"

    community_dir = utils.clone_source(COMMUNITY_URL, workdir, 'community')

    if resource_type == 'rpms':
        projects, project_dict = project_parser.parse_projects(community_dir + '/sig/')

        target_releases = utils.parse_yaml_list(config_options['release_list'], keyword='releases')

        rpms_dict = rpm_parser.process_rpms(target_releases, project_dict)

        for rpm_list in rpms_dict.values():
            engine = db.init_connections(config_options, 'openEuler-rpms')
            db.add_rpms(rpm_list, engine)

    elif resource_type == 'sigs':
        sigs = project_parser.parse_sigs(community_dir + '/sig/')

        for sig in sigs:
            engine = db.init_connections(config_options, 'openEuler-rpms')
            db.add_sig(sig, engine)


def do_list(resource_type, config_options, release_name=None, sig_name=None, arch=None, api_call=False):
    engine = db.init_connections(config_options, 'openEuler-rpms')

    if resource_type == 'rpms':
        for option in [(release_name, 'release name'),
                       (sig_name, 'sig name'),
                       (arch, 'architecture')]:
             utils.check_option(option[0], option[1])

        valid_arch = ['x86_64', 'aarch64', 'all']
        if arch not in valid_arch:
            err_str = 'Should provide choose a valid arch among: [x86_64, aarch64, all] ...'
            print(err_str)
            if not api_call:
                sys.exit(1)
            else:
                return err_str

        rpms = db.query_rpms(engine, sig_name, release_name, arch)

        return rpms

    elif resource_type == 'sigs':
        sigs = db.query_sigs(engine)

        return sigs



def load(resource_type, config_file):
    config_options = utils.check_and_load_config(config_file)

    do_load(resource_type, config_options)


def do_get(resource_type, resource_id, config_options):
    engine = db.init_connections(config_options, 'openEuler-rpms')

    if resource_type == 'sig':
        sig = db.query_sig(engine, resource_id)

        return sig

    elif resource_type == 'rpm':
        rpms = db.query_rpm(engine, resource_id)

        tb = pt.PrettyTable()
        tb.field_names = ["Package Name", "SIG", "Release", "Package Group", "Requires", "Provides", "Arch"]

        for rpm in rpms:
            tb.add_row([rpm.name, rpm.sig, rpm.oe_release, rpm.group, rpm.requires, rpm.provides, rpm.arch])

        print(tb)


@app.route("/sigs/<signame>")
def get_sig(signame):
    sig = do_get('sig', signame, config_options)
    return sig.to_dict()


@app.route("/sigs")
def list_sigs():
    args = request.args
    detailed = args.get('detailed')

    if detailed in ('True', 'true'):
        detailed = True
    else:
        detailed = False

    sigs = do_list('sigs', config_options, api_call=True)
    sig_list = []
    for sig in sigs:
        if detailed:
            sig_list.append(sig.to_dict())
        else:
            sig_list.append(sig.name)
    return {'sigs': sig_list}


@app.route("/rpms")
def list_rpms():
    args = request.args
    arch = args.get('arch')
    sig = args.get('sig')
    detailed = args.get('detailed')
    release = args.get('release')

    if detailed in ('True', 'true'):
        detailed = True
    else:
        detailed = False

    if not all([arch, sig, release]):
        return 'Should provide arch, sig and release to list rpms ...'

    rpms = do_list('rpms', config_options, release_name=release, sig_name=sig,
                   arch=arch, api_call=True)

    rpm_list = []
    if detailed:
        for rpm in rpms:
            rpm_list.append(rpm.to_dict())
    else:
        for rpm in rpms:
            rpm_list.append({'short-name': rpm.short_name})
    return {'rpms': rpm_list}


