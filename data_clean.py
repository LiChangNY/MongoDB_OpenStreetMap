import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
postcode = re.compile( r'^7(0|6)(\d{3})*')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        
        node["created"] = {}        
        for attribute in element.attrib: 
            if attribute in CREATED:   
                node["created"][attribute] = element.get(attribute)
            #create "pos" array for geo info
            elif attribute == "lat" or attribute == "lon":
                node["pos"] = []
                node["pos"].append(float(element.get("lat")))
                node['pos'].append(float(element.get("lon")))
            else: 
                node[attribute] = element.get(attribute)
                node['type'] = element.tag
        
        if element.find("tag") is not None:
            for tag in element.iter("tag"):
                sets = tag.attrib
                key = sets["k"]
                value = sets["v"]
                a = problemchars.search(key)          
                b = re.match("addr:", key)
                #ignore special characters
                if a:
                    continue
                #avoid override value of "node" and "way"
                elif key == 'type':  
                    continue
                #ignore tag containing two colons
                elif len(re.findall(":", key)) == 2:
                    continue
                #create dictionary of address                
                elif b:
                    if 'address' not in node.keys(): 
                        node['address'] = {}                
                    second_key = key.split(":")[1]
                    #extract street name
                    if second_key == 'street' and len(re.findall(',', value)) > 0:
                        node['address'][second_key] = value.split(',')[1]
                    #remove inaccurate postcodes
                    elif second_key == 'postcode' and postcode.search(value):
                        node['address'][second_key] = value
                    elif second_key != 'postcode':
                        node['address'][second_key] = value
                #split tag containing one colon to a new pair
                elif len(re.findall(":", key)) == 1:
                    node[key] = value                               
                else: 
                    node[key] = value
        
        #transform "way" info under node
        if element.tag == "way" :
            node["node_refs"] = []
            for tag in element.iter("nd"):
                sets = tag.attrib
                node['node_refs'].append(sets['ref'])  
                
        return node
            
    else:
        return None

def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data
    
process_map('ho-chi-minh-city_vietnam.osm', pretty = False)