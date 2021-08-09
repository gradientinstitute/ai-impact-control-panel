import toml
import namedtupled


def parse_config(f, build_tuple=True):
    parsed = toml.loads(f.read())
    cfg = namedtupled.map(parsed) if build_tuple else parsed
    return cfg
