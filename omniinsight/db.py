import json
import sqlalchemy
from sqlalchemy import Column, String, Text, create_engine, or_, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy_utils import database_exists, create_database


from omniinsight.objs import RpmData, SigData


Base = declarative_base()


class RPMS(Base):
    __tablename__ = 'rpms'

    id = Column(String(255), primary_key=True)
    name = Column(String(255))
    short_name = Column(String(255))
    arch = Column(String(32))
    group = Column(String(255))
    description = Column(Text)
    requires = Column(LONGTEXT)
    provides = Column(LONGTEXT)
    oe_release = Column(String(255))
    sig = Column(String(255))
    project = Column(String(255))


class SIGS(Base):
    __tablename__ = 'sigs'

    name = Column(String(255), primary_key=True)
    description = Column(Text)
    mentors = Column(Text)
    maintainers = Column(Text)
    committers = Column(Text)


def rpm_mapper(db_obj):
    rpm_obj = RpmData(db_obj.name)
    rpm_obj.id = db_obj.id
    rpm_obj.short_name = db_obj.short_name
    rpm_obj.arch = db_obj.arch
    rpm_obj.group = db_obj.group
    rpm_obj.description = db_obj.description
    rpm_obj.oe_release = db_obj.oe_release
    rpm_obj.sig = db_obj.sig
    rpm_obj.project = db_obj.project
    rpm_obj.requires = json.loads(db_obj.requires)
    rpm_obj.provides = json.loads(db_obj.provides)

    return rpm_obj


def sig_mapper(db_obj):
    sig_obj = SigData(db_obj.name)
    sig_obj.description = db_obj.description
    sig_obj.mentors = json.loads(db_obj.mentors)
    sig_obj.maintainers = json.loads(db_obj.maintainers)
    sig_obj.committers = json.loads(db_obj.committers)

    return sig_obj


def init_connections(config_options, database):
    PREFIX = 'mysql+pymysql://'
    engine_url = '%s%s:%s@%s:%s/%s' % (
        PREFIX, config_options['db_user'], config_options['db_password'],
        config_options['db_server'], config_options['db_port'], database)
    return create_engine(engine_url)


def prepare_database(config_options, database):
    engine = init_connections(config_options, database)

    # Check if the configured database exists
    if not database_exists(engine.url):
        print('Creating database: %s ...' % database)
        create_database(engine.url)
    else:
        print('Using existing database: %s ...' % database)

    # Check if the rpms, sigs table exists
    if not sqlalchemy.inspect(engine).has_table('rpms'):
        Base.metadata.create_all(engine)

    if not sqlalchemy.inspect(engine).has_table('sigs'):
        Base.metadata.create_all(engine)


def add_rpm(rpm, engine):
    new_rpm = RPMS(
        id=rpm.id, name=rpm.name, arch=rpm.arch, short_name=rpm.short_name,
        group=rpm.group, description=rpm.description,
        oe_release=rpm.oe_release, sig=rpm.sig, project=rpm.project,
        requires=json.dumps(rpm.requires), provides=(json.dumps(rpm.provides)))
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    try:
        session.add(new_rpm)
        session.commit()
    except Exception:
        pass
    session.close()


def add_rpms(rpms, engine):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    existed_records = []
    rpm_count = 0
    for rpm in rpms:
        if rpm.id in existed_records:
            continue
        else:
            existed_records.append(rpm.id)
        new_rpm = RPMS(
            id=rpm.id, name=rpm.name, arch=rpm.arch, short_name=rpm.short_name,
            group=rpm.group, description=rpm.description,
            oe_release=rpm.oe_release, sig=rpm.sig, project=rpm.project,
            requires=json.dumps(rpm.requires), provides=(json.dumps(rpm.provides)))
        rpm_count += 1

        session.add(new_rpm)

        # batch commit for every 50 records
        if rpm_count % 1000 == 0:
            session.commit()

    try:
        session.commit()
    except Exception:
        pass
    session.close()


def query_rpms(engine, sig, release, arch):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    result = []

    if arch == 'aarch64':
        db_objs = session.query(RPMS).filter(RPMS.sig == sig).\
            filter(RPMS.oe_release == release).\
            filter(or_(RPMS.arch == 'aarch64', RPMS.arch == 'noarch')).\
            all()
    elif arch == 'x86_64':
        db_objs = session.query(RPMS).filter(RPMS.sig == sig). \
            filter(RPMS.oe_release == release). \
            filter(or_(RPMS.arch == 'x86_64', RPMS.arch == 'noarch')). \
            all()
    else:
        db_objs = session.query(RPMS).filter(RPMS.sig == sig). \
            filter(RPMS.oe_release == release). \
            all()

    for db_obj in db_objs:
        result.append(rpm_mapper(db_obj))

    return result


def query_rpm(engine, name):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    result = []

    db_objs = session.query(RPMS).filter(RPMS.name == name).all()
    for db_obj in db_objs:
        result.append(rpm_mapper(db_obj))

    return result


def add_sig(sig, engine):
    new_sig = SIGS(
        name=sig.name, description=sig.description,
        mentors=json.dumps(sig.mentors),
        maintainers=json.dumps(sig.maintainers),
        committers=json.dumps(sig.committers)
    )
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    try:
        session.add(new_sig)
        session.commit()
    except Exception:
        pass
    session.close()


def query_sigs(engine):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    result = []

    db_objs = session.query(SIGS).all()

    for db_obj in db_objs:
        result.append(sig_mapper(db_obj))

    return result


def query_sig(engine, name):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    db_obj = session.query(SIGS).filter(SIGS.name == name).one()
    return sig_mapper(db_obj)
