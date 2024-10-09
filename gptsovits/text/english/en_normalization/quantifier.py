import re
from num2words import num2words

UNIT_MAP = {
    'm': 'meter',
    'm²': 'square meter',
    'm^2': 'square meter',
    '㎡': 'square meter',
    'm³': 'cubic meter',
    'm^3': 'cubic meter',
    'mm': 'millimeter',
    'mm²': 'square millimeter',
    'mm^2': 'square millimeter',
    'mm³': 'cubic millimeter',
    'mm^3': 'cubic millimeter',
    'cm': 'centimeter',
    'cm²': 'square centimeter',
    'cm^2': 'square centimeter',
    'cm³': 'cubic centimeter',
    'cm^3': 'cubic centimeter',
    'km': 'kilometer',
    'in': 'inch',
    'ft': 'foot',
    'yd': 'yard',
    'mi': 'mile',
}

RE_TO_RANGE = re.compile(
    r'((-?)((\d+)(\.\d+)?)|(\.(\d+)))(%|°C|℃|cm2|cm²|cm3|cm³|cm|db|ds|kg|km|m2|m²|m³|m3|ml|m|mm|s)[~]((-?)((\d+)(\.\d+)?)|(\.(\d+)))(%|°C|℃|cm2|cm²|cm3|cm³|cm|db|ds|kg|km|m2|m²|m³|m3|ml|m|mm|s)')

def replace_to_range(match) -> str:
    """
    Args:
        match (re.Match)
    Returns:
        str
    """
    result = match.group(0).replace('~', ' to ')
    return result

RE_DIMENSION = re.compile(r'(\d+(\.\d+)?)\s*([a-zA-Z²³㎡^0-9]+)\s*[*|×]\s*(\d+(\.\d+)?)\s*([a-zA-Z²³㎡^0-9]+)')

def replace_dimension(match) -> str:
    num1 = float(match.group(1)) if '.' in match.group(1) else int(match.group(1))
    unit1 = match.group(3)
    num2 = float(match.group(4)) if '.' in match.group(4) else int(match.group(4))
    unit2 = match.group(6)

    return f"{num1}{unit1} by {num2}{unit2}"

def replace_measure(sentence) -> str:
    for q_notation, replacement in UNIT_MAP.items():
        pattern = rf'((?:\d+(?:\.\d+)?|[⁰¹²³⁴⁵⁶⁷⁸⁹]+))\s*{re.escape(q_notation)}'
        sentence = re.sub(pattern, rf'\1 {replacement}', sentence)
    return sentence

def quantifier_normalize(text):
    text = RE_TO_RANGE.sub(replace_to_range, text)
    text = RE_DIMENSION.sub(replace_dimension, text)
    text = replace_measure(text)
    return text