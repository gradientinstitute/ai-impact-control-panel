import toml
import namedtupled


def parse_config(f):
    parsed = toml.loads(f.read())
    cfg = namedtupled.map(parsed)
    return cfg
