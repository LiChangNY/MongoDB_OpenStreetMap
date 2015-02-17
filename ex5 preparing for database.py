#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        # YOUR CODE HERE
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
                    
                #ignore tag with two colons
                elif len(re.findall(":", key)) == 2:
                    continue
                    
                #create "address" array
                elif b:
                    if 'address' not in node.keys():
                        node['address'] = {}
                    second_key = key.split(":")[1]
                    node['address'][second_key] = value            
                
                #split tag containing one colon to a new pair
                elif len(re.findall(":", key)) == 1:
                    node[key] = value                               
                else: 
                    node[key] = value
        
        #turn "way" into a new key under node
        if element.tag == "way" :
            node["node_refs"] = []
            for tag in element.iter("nd"):
                sets = tag.attrib
                node['node_refs'].append(sets['ref'])  
                
        pprint.pprint(node)
        return node
    
    else:
        return None

def process_map(file_in, pretty = False):
    # You do not need to change this file
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

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    data = process_map('example.osm', True)
    #pprint.pprint(data)
    
    assert data[0] == {
                        "id": "261114295", 
                        "visible": "true", 
                        "type": "node", 
                        "pos": [
                          41.9730791, 
                          -87.6866303
                        ], 
                        "created": {
                          "changeset": "11129782", 
                          "user": "bbmiller", 
                          "version": "7", 
                          "uid": "451048", 
                          "timestamp": "2012-03-28T18:31:23Z"
                        }
                      }
    assert data[-1]["address"] == {
                                    "street": "West Lexington St.", 
                                    "housenumber": "1412"
                                      }
    assert data[-1]["node_refs"] == [ "2199822281", "2199822390",  "2199822392", "2199822369", 
                                    "2199822370", "2199822284", "2199822281"]

if __name__ == "__main__":
    test()