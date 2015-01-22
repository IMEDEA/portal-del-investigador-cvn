# -*- encoding: UTF-8 -*-

#
#    Copyright 2014-2015
#
#      STIC-Investigación - Universidad de La Laguna (ULL) <gesinv@ull.edu.es>
#
#    This file is part of CVN.
#
#    CVN is free software: you can redistribute it and/or modify it under
#    the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    CVN is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with CVN.  If not, see
#    <http://www.gnu.org/licenses/>.
#

from cvn import settings as st_cvn
from iso3166 import countries
import datetime
import string
import sys
import logging

logger = logging.getLogger('cvn')


def _parse_duration(duration):
    """Input: Duration/Item node
       Example: CvnItem/Date/Duration/Item
    """
    if duration is None:
        return None
    duration = duration.text
    duracion = 0
    number = ''
    for item in duration[1:]:
        if item.isdigit():
            number = item
        else:
            if item == 'Y':
                duracion += int(unicode(number)) * 365
            if item == 'M':
                duracion += int(unicode(number)) * 30
            if item == 'D':
                duracion += int(unicode(number))
    return duracion


def _parse_segregated_date(xml):
    if xml is None:
        return None
    date = xml.find('DayMonthYear/Item')
    if date is not None:
        date = date.text.split('-')
        return datetime.date(int(date[0]), int(date[1]), int(date[2]))
    date = xml.find('MonthYear/Item')
    if date is not None:
        date = date.text.split('-')
        return datetime.date(int(date[0]), int(date[1]), 1)
    date = xml.find('Year/Item')
    if date is not None:
        return datetime.date(int(date.text), 1, 1)
    return None


def _parse_unitary_date(xml):
    date = xml.text.split('-')
    return datetime.date(int(date[0]), int(date[1]), int(date[2]))


def _enddate_to_duration(node, fecha_inicio):
    duration = None
    fecha_fin = _parse_segregated_date(node)
    if fecha_inicio is not None and fecha_fin is not None:
        delta = fecha_fin - fecha_inicio
        duration = delta.days
    return fecha_fin, duration


def _duration_to_enddate(node, fecha_inicio):
    duration = _parse_duration(node)
    if fecha_inicio is not None and duration is not None:
        fecha_fin = (fecha_inicio + datetime.timedelta(days=duration))
        return fecha_fin, duration
    return None, None


def _parse_place(place_node):
    """Input: a Place node"""
    place = ""
    region = place_node.find("Region/Name/Item")
    country = place_node.find("CountryCode/Item")
    if region is not None:
        place += region.text
    if region is not None and country is not None:
        place += ", "
    if country is not None:
        try:
            place += countries.get(country.text).name
        except KeyError:
            logger.error(u'%s: Código de País no válido' % country.text)
    return place


def _get_produccion_from_code(code, subtype):
    if code == '':
        return None
    if code == 'TesisDoctoral' and subtype != 'TesisDoctoral':
        return None
    if code == 'Publicacion':
        if subtype not in [u'Articulo', u'Libro', u'Capitulo']:
            return None
        code = subtype
    return getattr(sys.modules['cvn.models'], code)


def parse_scope(tree_xml):
    """Input: Scope node
       Example: CvnItem/Link/Scope
    """
    data_cvn = {}
    if tree_xml:
        data_cvn['ambito'] = unicode(st_cvn.SCOPE[tree_xml.find(
            'Type/Item').text.strip()])
        if data_cvn['ambito'] == u'Otros' and tree_xml.find('Others/Item'):
            data_cvn['otro_ambito'] = unicode(tree_xml.find(
                'Others/Item').text.strip())
    return data_cvn


def parse_title(xml):
    """Input: CvnItem node"""
    title = None
    node = xml.find('Title/Name/Item')
    if node is not None:
        title = unicode(node.text.strip(string.whitespace + '.,;"\''))
    return title


def parse_nif(xml):
    """Input: root node"""
    if xml is None:
        return ''
    nif = ''
    id_node = xml.find(
        'Agent/Identification/PersonalIdentification/OfficialId')
    if id_node is None:
        return nif
    nif_node = id_node.find('DNI/Item')
    if nif_node is None:
        nif_node = id_node.find('NIE/Item')

    if nif_node is not None:
        nif = nif_node.text.strip()

    return nif


def parse_authors(author_list):
    """Input: A list of Author nodes"""
    authors = ''
    for author in author_list:
        author_item = ''
        author_name = author.find("GivenName/Item")
        if author_name is not None and author_name.text:
            author_item = unicode(author_name.text.strip())
        author_ffname = author.find("FirstFamilyName/Item")
        if author_ffname is not None and author_ffname.text:
            author_item += ' ' + unicode(author_ffname.text.strip())
        author_sfname = author.find("SecondFamilyName/Item")
        if author_sfname is not None and author_sfname.text:
            author_item += ' ' + unicode(author_sfname.text.strip())
        signature = author.find("Signature/Item")
        if signature is not None and signature.text:
            if author_item:
                authors += unicode(
                    author_item + ' (' + signature.text.strip() + '); ')
            else:
                authors += unicode(signature.text.strip() + '; ')
        elif author_item:
            authors += author_item + '; '
    return authors[:-2] if authors else authors


def _parse_produccion_type(xml):
    """Input: CvnItem node"""
    if xml is None:
        return ''
    cvn_key = xml.find('CvnItemID/CVNPK/Item').text.strip()
    if cvn_key not in st_cvn.CVNITEM_CODE:
        return ''
    return st_cvn.CVNITEM_CODE[cvn_key]


def _parse_produccion_subtype(xml):
    """Input: CvnItem node"""
    if xml is None:
        return ''
    subtype = xml.find('Subtype/SubType1/Item')
    if subtype is None:
        return ''
    subtype = subtype.text.strip()
    if subtype in st_cvn.CVNITEM_SUBTYPE_CODE:
        return st_cvn.CVNITEM_SUBTYPE_CODE[subtype]
    return ''


def parse_publicacion_location(xml):
    """Input: Location node"""
    data = {}
    if xml:
        volume = xml.find('Volume/Item')
        if volume is not None and volume.text is not None:
            data['volumen'] = volume.text.strip()
        number = xml.find('Number/Item')
        if number is not None and number.text is not None:
            data['numero'] = number.text.strip()
        page = xml.find('InitialPage/Item')
        if page is not None and page.text is not None:
            data['pagina_inicial'] = page.text.strip()
        page = xml.find('FinalPage/Item')
        if page is not None and page.text is not None:
            data['pagina_final'] = page.text.strip()
    return data


def parse_date(xml):
    """Input: date node"""
    if xml is None:
        return None
    # Node of type Date > OnlyDate
    node = xml.find('OnlyDate')
    if node is not None:
        return _parse_segregated_date(node)
    # Node of type Date > StartDate
    node = xml.find('StartDate')
    if node is not None:
        return _parse_segregated_date(node)
    # Node of type Date > Item
    node = xml.find('Item')
    if node is not None:
        return _parse_unitary_date(node)
    return None


def parse_date_interval(xml):
    """Input: date node"""
    if xml is None:
        return None, None, None
    # Get start date
    fecha_inicio = parse_date(xml)
    # Get end date
    fecha_fin_1, duracion_1 = _enddate_to_duration(
        xml.find('EndDate'), fecha_inicio)
    # Get duration
    fecha_fin_2, duracion_2 = _duration_to_enddate(
        xml.find('Duration/Item'), fecha_inicio)

    if fecha_fin_2 is None:
        fecha_fin = fecha_fin_1
        duracion = duracion_1
    elif fecha_fin_1 is None:
        fecha_fin = fecha_fin_2
        duracion = duracion_2
    elif fecha_fin_1 > fecha_fin_2:
        fecha_fin = fecha_fin_1
        duracion = duracion_1
    else:
        fecha_fin = fecha_fin_2
        duracion = duracion_2
    return fecha_inicio, fecha_fin, duracion


def parse_produccion_id(node_list):
    """Input: node_list is a list of ExternalPK nodes (ExternalPK nodes contain
       different identifiers for produccion nodes.
       Output: A dictionary with the PRODUCCION_ID_CODEs found
    """
    prods = {i: None for i in st_cvn.PRODUCTION_ID_CODE.values()}

    for node in node_list:
        prods[node.find('Type/Item').text] = node.find('Code/Item').text

    return prods


def parse_economic(node_list):
    """Input: a list of EconomicDimension nodes"""
    data_cvn = {}
    for item in node_list:
        economic = item.find('Value').attrib['code']
        data_cvn[st_cvn.ECONOMIC_DIMENSION[economic]] = unicode(item.find(
            'Value/Item').text.strip())
    return data_cvn


def parse_places(node_list):
    """Input: a list of Place nodes
       Output: main_place with the place of creation/registration,
               extended_place with a list of places where the item
               is registered/operated
    """
    main_place = None
    extended_place = u""
    for item in node_list:
        country = item.find("CountryCode")
        if country.attrib['code'] == st_cvn.PRIORITY_COUNTRY:
            main_place = _parse_place(item)
        elif country.attrib['code'] == st_cvn.EXTENDED_COUNTRY:
            extended_place += _parse_place(item) + "; "
    return main_place, extended_place.strip('; ')


def parse_entities(node_list):
    operators = u""
    entities = {i.value: None for i in st_cvn.Entity}
    for item in node_list:
        entity = item.find("EntityName")
        # Most entities come once, so we just save the content to a dict key
        if entity.attrib['code'] != st_cvn.Entity.OPERATOR.value:
            entities[entity.attrib['code']] = entity.find("Item").text
        # The entity operator (an entity that operates a patent) can come
        # more than once, so we concatenate the occurrence.
        else:
            operators += entity.find("Item").text + "; "
    if operators:
        entities[st_cvn.Entity.OPERATOR.value] = operators.strip('; ')
    return entities


def parse_dedication_type(node):
    if node is not None:
        return (st_cvn.DedicationType(node.text)
                == st_cvn.DedicationType.TOTAL)
    else:
        return None


def parse_filters(node_list):
    filters = {i.value: None for i in st_cvn.FilterCode}
    for item in node_list:
        filter_name = item.find("Value")
        data = filter_name.find("Item").text
        filters[filter_name.attrib['code']] = data
        if data == 'OTHERS':
            filters[filter_name.attrib['code']] = item.find("Others/Item").text
        else:  # Get the key of corresponding hash
            dict = st_cvn.SUBJECT_TYPE
            if filter_name.attrib['code'] == st_cvn.FilterCode.PROGRAM.value:
                dict = st_cvn.PROGRAM_TYPE
            filters[filter_name.attrib['code']] = dict.keys()[
                dict.values().index(unicode(data))]

    return filters


def parse_cvnitem_to_class(cvnitem):
    code = _parse_produccion_type(cvnitem)
    subtype = _parse_produccion_subtype(cvnitem)
    return _get_produccion_from_code(code, subtype)
