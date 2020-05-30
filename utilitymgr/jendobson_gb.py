"""
Parse GreenButton XML (within zipfile)

Copied from https://github.com/JenDobson/greenbutton because the PyPI
package is out of date.
"""

import datetime
import xml.etree.ElementTree as ET
import pandas as pd


ns = {'default': 'http://www.w3.org/2005/Atom',
      'reading': 'http://naesb.org/espi'}


def get_interval_blocks(root):
    """ Return list of interval blocks """
    return root.findall('default:entry/default:content/reading:IntervalBlock', ns)


def get_interval_readings(interval_block):
    """ Return list of interval readings """
    return interval_block.findall('reading:IntervalReading', ns)


def parse_reading(interval_reading_node):
    start = datetime.datetime.fromtimestamp(
        int(interval_reading_node.find('reading:timePeriod/reading:start', ns).text))
    duration = datetime.timedelta(
        seconds=int(interval_reading_node.find('reading:timePeriod/reading:duration', ns).text))
    value = int(interval_reading_node.find('reading:value', ns).text)
    return start, duration, value


def dataframe_from_xml(xmlfile):
    tree = ET.parse(xmlfile)
    root = tree.getroot()

    interval_blocks = get_interval_blocks(root)

    readings = []

    for interval_block in interval_blocks:
        for interval_reading in get_interval_readings(interval_block):
            readings.append(parse_reading(interval_reading))

    result = pd.DataFrame(readings, columns=['Start Time', 'Duration', 'Wh'])
    dst_offset = int(root.find('default:entry/default:content/reading:LocalTimeParameters/reading:dstOffset', ns).text)
    tz_offset = int(root.find('default:entry/default:content/reading:LocalTimeParameters/reading:tzOffset', ns).text)
    result['Start Time'] += datetime.timedelta(seconds=(dst_offset + tz_offset))
    return result

