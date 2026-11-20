import re

from django import template

register = template.Library()

# READABLE HEADINGS, WITH UNITS, FOR KNOWN SCHEMA COLUMNS. ANY OTHER KEY (E.G. A USER ALIAS) KEEPS ITS OWN NAME.
COLUMN_LABELS = {
    'ra': 'RA (deg)',
    'decl': 'Dec (deg)',
    'cone_id': 'Cone ID',
    'UTC': 'Alert time (UTC)',
    'psfFlux': 'Latest flux (nJy)',
    'latest_psfFlux': 'Latest flux (nJy)',
    'lastDiaSourceMjdTai': 'Last detected (MJD)',
    'firstDiaSourceMjdTai': 'First detected (MJD)',
    'nDiaSources': 'Detections',
    'absMag': 'Peak absolute mag',
    'sherlock': 'Sherlock class',
    'days ago': 'Days ago',
    'days since': 'Days since',
    'classification': 'Classification',
    'classdict': 'Classification data',
}

# BAND COLUMNS FOLLOW ONE PATTERN, E.G. r_psfFlux -> "r flux (nJy)"
BAND_COLUMN_LABELS = {
    'psfFlux': '{band} flux (nJy)',
    'psfFluxMean': '{band} mean flux (nJy)',
    'psfFluxMeanErr': '{band} mean flux error (nJy)',
    'latestMJD': '{band} latest (MJD)',
}
BAND_COLUMN_PATTERN = re.compile(r'^([ugrizy])_(%s)$' % '|'.join(BAND_COLUMN_LABELS))


@register.filter
def keyvalue(dict, key):
    try:
        return dict[key]
    except (KeyError, TypeError):
        return ''


@register.filter
def replace(value, arg):
    """
    Replacing filter
    Use `{{ "aaa"|replace:"a|b" }}`
    """
    if len(arg.split('|')) != 2:
        return value

    what, to = arg.split('|')
    return value.replace(what, to)


@register.filter
def is_float(value):
    return isinstance(value, float)


@register.filter
def column_label(key):
    """
    Readable heading, with units, for a results-table column
    Use `{{ key|column_label }}`
    """
    if key in COLUMN_LABELS:
        return COLUMN_LABELS[key]
    bandMatch = BAND_COLUMN_PATTERN.match(str(key))
    if bandMatch:
        return BAND_COLUMN_LABELS[bandMatch.group(2)].format(band=bandMatch.group(1))
    return key


@register.filter
def column_tooltip(schema, key):
    """
    Header tooltip: the column name, then its schema description if there is one
    Use `{{ schema|column_tooltip:key }}`
    """
    description = keyvalue(schema, key)
    if not description:
        return key
    return f'{key}: {description}'
