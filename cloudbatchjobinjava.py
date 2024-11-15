import json
import re

from flask import render_template

commonJavaKeyWords = [
#    "System", "out", "println", "String", "Integer", "Double", "Boolean", "ArrayList", "HashMap", "HashSet", "List", "Map", "Set",
#    "public", "private", "protected", "static", "final", "void", "int", "double", "float", "char", "boolean", "long", "short", "byte",
#    "new", "return", "this", "super", "class", "interface", "extends", "implements", "package", "import", "try", "catch", "finally",
#    "throw", "throws", "synchronized", "volatile", "transient", "abstract", "enum", "instanceof", "assert", "break", "case", "continue",
#    "default", "do", "else", "for", "if", "goto", "switch", "while", "native", "strictfp"
]
classMethodsforOnStart = {}
classMethodsforOnProcess = {}
classMethodsforOnEnd = {}

def cloudbatchjobinjava(application, requestid=None, requestContentInJSON=None):
    read_javap_result(application)
    if requestContentInJSON:
        requestContentInJSON = json.dump(requestContentInJSON)
        return render_template('cloudbatchjobinjava.html', requestid=requestid, requestContentInJSON=json.dumps(requestContentInJSON, indent=4))
    else:
        return render_template('cloudbatchjobinjava.html')

def check_and_generate_keywords_(line, cursor_pos, method):
    match = re.search(r'(\w+)\.$', line[:cursor_pos])
    if match:
        class_name = match.group(1)
        if method == 'onstart':
            if class_name in classMethodsforOnStart:
                filtered_list = classMethodsforOnStart[class_name]
        elif method == 'onprocess':
            if class_name in classMethodsforOnProcess:
                filtered_list = classMethodsforOnProcess[class_name]
        elif method == 'onend':
            if class_name in classMethodsforOnEnd:
                filtered_list = classMethodsforOnEnd[class_name]
        else:
            filtered_list = []
    else:
        filtered_list = [kw for kw in commonJavaKeyWords if kw.startswith(line[cursor_pos:])]
    
    return filtered_list


def read_javap_result(app):
    try:
        result = {}
        file_path = app.config['path_of_interfaceOnly_javap']
        tempClassName = ''
        tempClass = []
        with open(file_path, 'r') as file:
            for line in file:
                content = line.strip()
                # detect the class
                if ' class ' in content and ' {' in content:
                    tempClassName = content.replace('public class ', '').replace(' {', '').strip()
                    tempClassName = tempClassName.split('.')[-1]
                    result[tempClassName] = {}
                    tempClass = result[tempClassName]
                    tempClass['variables'] = set()
                    tempClass['methods'] = set()
                if len(content) > 0 and 'public' in content and tempClassName not in content:
                    if '(' not in content:
                        tempClass['variables'].add(content.replace('public ', '').replace(';', ''))
                    else:  
                        tempMethod = content.replace('public ', '').replace(';', '')
                        tempMethod = tempMethod[:tempMethod.index(')') + 1]
                        tempMethod = tempMethod.split(' ')[-1]
                        tempClass['methods'].add(tempMethod)

        result.pop('ForFutureData')
        result.pop('Order')
        result.pop('Profile')
        result.pop('Main')
        result.pop('Action>')

        for k, v in result.items():
            print(f"Class: {k}")
            print(f"Variables: {v['variables']}")
            print(f"Methods: {v['methods']}")
            print() 
            if v['methods'] is not None:
                classMethodsforOnStart[k] = list(v['methods']) + list(v['variables'])
                if(k == 'FutureDataStructure'):
                    classMethodsforOnProcess['data'] = list(v['methods']) + list(v['variables'])
                else:
                    classMethodsforOnProcess[k] = list(v['methods']) + list(v['variables'])
                classMethodsforOnEnd[k] = list(v['methods']) + list(v['variables'])
            
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")