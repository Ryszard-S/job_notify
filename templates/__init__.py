from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader('templates'),
    autoescape=select_autoescape()
)


def datetimeformat(value, format='%d-%m-%Y %H:%M'):
    return value.strftime(format)


env.filters['datetime'] = datetimeformat
