import dnf

import omniinsight.objs as objs


ARCHS = ['x86_64', 'aarch64']
REPO_GROUPS = ['OS', 'everything', 'EPOL']
OE_REPO_BASE = 'http://repo.openeuler.org/'
EPOL_WITH_MAIN = ['openEuler-21.09', 'openEuler-22.03-LTS', 'openEuler-20.03-LTS-SP2', 'openEuler-20.03-LTS-SP3']


def read_from_remote_repo(release, group, arch):
    base = dnf.Base()
    conf = base.conf
    conf.cachedir = '/tmp/omni-insight-cache/'
    conf.logdir = '/var/log/omni-insight/'

    if group == 'EPOL' and release in EPOL_WITH_MAIN:
        repo_url = OE_REPO_BASE + release + '/' + group + '/main/' + arch + '/'
    else:
        repo_url = OE_REPO_BASE + release + '/' + group + '/' + arch + '/'

    print('Processing Repo: ' + repo_url)
    base.repos.add_new_repo(release, conf, baseurl=[repo_url])

    base.fill_sack()
    query = base.sack.query().available()

    return query.run()


def parse_rpm(pkg, release, group, project_dict):
    pkg_name = '-'.join([pkg.name, pkg.version, pkg.release]) + '.' + pkg.arch + '.rpm'

    print('Processing RPM: ' + pkg_name)
    rpm = objs.RpmData(pkg_name)

    # Form a unique name from pkg name and release to be used as primary key in DB,
    # this can avoid same rpm for different releases
    rpm.id = rpm.name + '_' + release

    rpm.project = pkg.source_name
    rpm.arch = pkg.arch
    rpm.group = group
    rpm.oe_release = release
    rpm.description = pkg.description
    rpm.short_name = pkg.name
    sig = project_dict.get(rpm.project)
    if sig:
        rpm.sig = sig

    for require in pkg.requires:
        rpm.requires.append(str(require))

    for provide in pkg.provides:
        rpm.provides.append(str(provide))

    return rpm


def process_rpms(releases, project_dict):
    # Build a rpms dict with releases as their key, the value will be
    # filled later with all rpms from that release
    rpms_dict = dict.fromkeys(releases)
    for release in releases:
        rpm_list = []
        for group in REPO_GROUPS:
            for arch in ARCHS:
                pkgs = read_from_remote_repo(release, group, arch)

                for pkg in pkgs:
                    pkg_rpm = parse_rpm(pkg, release, group, project_dict)
                    rpm_list.append(pkg_rpm)

        rpms_dict[release] = rpm_list

    return rpms_dict
