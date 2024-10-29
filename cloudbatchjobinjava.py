import re

commonJavaKeyWords = [
    "System", "out", "println", "String", "Integer", "Double", "Boolean", "ArrayList", "HashMap", "HashSet", "List", "Map", "Set",
    "public", "private", "protected", "static", "final", "void", "int", "double", "float", "char", "boolean", "long", "short", "byte",
    "new", "return", "this", "super", "class", "interface", "extends", "implements", "package", "import", "try", "catch", "finally",
    "throw", "throws", "synchronized", "volatile", "transient", "abstract", "enum", "instanceof", "assert", "break", "case", "continue",
    "default", "do", "else", "for", "if", "goto", "switch", "while", "native", "strictfp"
]
classMethods = {
    "abc": ["method1", "method2", "method3"]
};


def check_and_generate_keywords_(line, cursor_pos):
    match = re.search(r'(\w+)\.$', line[:cursor_pos])
    if match:
        class_name = match.group(1)
        if class_name in classMethods:
            filtered_list = classMethods[class_name]
        else:
            filtered_list = []
    else:
        filtered_list = [kw for kw in commonJavaKeyWords if kw.startswith(line[cursor_pos:])]
    
    return filtered_list


def read_javap_result(file_path):
    try:
        tempClassName = ''
        tempClass = []
        with open(file_path, 'r') as file:
            for line in file:
                content = line.strip()
                # detect the class
                if ' class ' in content and ' {' in content:
                    tempClassName = content.replace('public class ', '').replace(' {', '').strip()
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
                        tempClass['methods'].add(tempMethod)

        result.pop('main.logiclibrary.ForFutureData')
        result.pop('tradelibrary.Order')
        result.pop('tradelibrary.Profile')
        result.pop('Main')
        result['public final class orderlibirary.Action extends java.lang.Enum<orderlibirary.Action>'].pop('methods')

        print(result)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")