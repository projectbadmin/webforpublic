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