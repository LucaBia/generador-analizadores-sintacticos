from readline import append_history_file
import tkinter as tk
from tkinter import CENTER, HORIZONTAL, filedialog
from tkinter import scrolledtext as st
from tkinter import messagebox as mb
from tkinter import ttk
import time
import re
import sys
import os
from afd import AFD

import json


# https://ssw.jku.at/Research/Projects/Coco/
# https://ssw.jku.at/Research/Projects/Coco/Doc/UserManual.pdf


nombre_compilador = ''

scanner_lineas = []
file_lines = []
tokens = []
tokens_filtrados = []

characters_extraidos = {}
keywords_extraidos = {}
tokens_expreg_extraidos = {}
symbols = {}

ignore_extraidos = {
    'char_numbers': [],
    'strings': [],
}
productions_extraidos = {}

noTerminalesNumber = []
noTerminales = []


characters = {
    ' ': ' ',
    '"': '"',
    '\'': '\'',
    '/': '/',
    '*': '*',
    '=': '=',
    '.': '.',
    '|': '|',
    '<': '<',
    '>': '>',
    '(': '(',
    ')': ')',
    '[': '[',
    ']': ']',
    '{': '{',
    '}': '}',
    'o': '+-',
    's': '@~!#$%^&_;:,?',
    'l': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
    'd': '0123456789',
}

keywords = {
    'COMPILER': 'COMPILER',
    'CHARACTERS': 'CHARACTERS',
    'KEYWORDS': 'KEYWORDS',
    'TOKENS': 'TOKENS',
    'PRODUCTIONS': 'PRODUCTIONS',
    'END': 'END',
    'EXCEPT': 'EXCEPT',
    'ANY': 'ANY',
    'CONTEXT': 'CONTEXT',
    'IGNORE': 'IGNORE',
    'PRAGMAS': 'PRAGMAS',
    'IGNORECASE': 'IGNORECASE',
    'WEAK': 'WEAK',
    'COMMENTS': 'COMMENTS',
    'FROM': 'FROM',
    'NESTED': 'NESTED',
    'SYNC': 'SYNC',
    'IF': 'IF',
    'out': 'out',
    'TO': 'TO',
    'NEWLINE': '\\n',
}

tokens_expreg = {
    'semantic_action': '«(.««a¦"»¦\'»±.»)',
    'attrs': '«<.««a¦"»¦\'»±.»>',
    'comment_block': '«/*««a¦"»¦\'»±*»/',
    'comment': '//««««l¦d»¦s»¦o»¦ »±',
    'char': '«\'«a¦"»±»\'',
    'string': '"«a¦\'»±"',
    'number': 'd«d»±',
    'ident': 'l«l¦d»±',
    'operator': 'o',
    'iteration': '{¦}',
    'option': '[¦]',
    'group': '(¦)',
    'or': '|',
    'final': '.',
    'assign': '=',
    'space': ' ',
}


def browseFiles():
    filename = filedialog.askopenfilename(initialdir = "./", title = "Select a File", filetypes = (("CocoL files", "*.atg"), ("all files", "*.*")))
    filename_splited = filename.split("/")
    filename_splited = filename_splited[len(filename_splited)-1]
    archivo1_ = "./" + filename_splited
    label_file_explorer.configure(text=archivo1_)
    archivo1.set(archivo1_)

def browseFiles2():
    filename = filedialog.askopenfilename(initialdir = "./", title = "Select a File", filetypes = (("Text files", "*.txt"), ("all files", "*.*")))
    filename_splited = filename.split("/")
    filename_splited = filename_splited[len(filename_splited)-1]
    archivo2_ = "./" + filename_splited
    label_file_explorer2.configure(text=archivo2_)
    archivo2.set(archivo2_)

def step():
    window.update_idletasks()
    progress['value'] += 20
    
    time.sleep(1)

def tipo_token(word):
    if word in keywords.values():
        return 'KEYWORD'
    elif word in [chr(number) for number in ignore_extraidos['char_numbers']] or word in ignore_extraidos['strings']:
        return 'IGNORE'
    else:
        for token_type, re in tokens_expreg.items():
            # Cualquier cosa menos "" ''
            if AFD(re.replace('a', '«««««««««««««««««l¦d»¦s»¦o»¦ »¦(»¦)»¦/»¦*»¦=»¦.»¦|»¦[»¦]»¦{»¦}»¦<»¦>»')).accepts(word, characters):
                return token_type
    return 'ERROR'

def centinela(line, line_index):
    analyzed_lines = 1
    line_position = 0
    current_line_recognized_tokens = []
    while line_position < len(line):
        current_token = None
        next_token = None
        avance = 0
        continuar = True
        while continuar:
            if current_token and next_token:
                if current_token['type'] != 'ERROR' and next_token['type'] == 'ERROR':
                    avance -= 1
                    continuar = False
                    break

            if line_position + avance > len(line):
                continuar = False
                break

            if line_position + avance <= len(line):
                # current_token = {
                #     'type': tipo_token(line[line_position:line_position + avance]),
                #     'value': line[line_position:line_position + avance],
                #     'line': line_index
                # }
                if line[line_position:line_position + avance + 1] in ['(.', '<.']:
                    current_token = {
                        'type': tipo_token(line[line_position:line_position + avance + 1]),
                        'value': line[line_position:line_position + avance + 1],
                        'line': line_index
                    }
                else:
                    current_token = {
                        'type': tipo_token(line[line_position:line_position + avance]),
                        'value': line[line_position:line_position + avance],
                        'line': line_index
                    }

            


            avance += 1

            if line_position + avance <= len(line):
                next_token = {
                    'type': tipo_token(line[line_position:line_position + avance]),
                    'value': line[line_position:line_position + avance],
                    'line': line_index
                }


        line_position = line_position + avance


        if current_token and current_token['type'] != 'ERROR':
            tokens.append(current_token)
            current_line_recognized_tokens.append(current_token)
        else:
            print("ERRORES ", current_token)

            if line_position == len(line) + 1 and len(current_line_recognized_tokens) != 0:
                tokens.append(current_token)

            # Si se llega al final de la linea y no se reconoce ningun token,
            # se agrega la siguiente linea y se vuelve a intentar.
            if line_position == len(line) + 1 and len(current_line_recognized_tokens) == 0:
                if line_index < len(file_lines) - 1:
                    new_line = line.replace('\\n', ' ') + ' ' + file_lines[line_index + 1].replace('\n', '\\n')
                    line_index += 1
                    analyzed_lines += centinela(new_line, line_index)

    return analyzed_lines

def cambio_simbolos(re):
    cont = 0
    closeK = []
    for pos, char in enumerate(re):
        if char == '{':
            cont += 1
        elif char == '}':
            closeK.append(pos)
            cont -= 1

    if cont != 0:
        return False

    re = re.replace('{', '«')
    re = re.replace('}', '»')
    re = re.replace('|', '¦')

    for i in range(len(closeK)):
        re = re[:closeK[i]+1+i] + '±' + re[closeK[i]+1+i:]

    return re

# pasa los keys de los characters a un solo digito
def formatear_characters(characters):
    options = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R']
    cont = 0
    keys = list(characters.keys())
    for i in range(len(characters)):

        symbols[keys[i]] = options[cont]
        characters[options[cont]] = characters.pop(keys[i])
        cont += 1

    return characters

# pasa los identificadores de los values de los tokens a un solo digito definido en formatear_characters
def formatear_tokens_exp(TOKENS_RE):
    # 'letter {letter|digit} EXCEPT KEYWORDS' ---> 'A«A¦B»±'
    options = ['S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    for key, val in TOKENS_RE.items():
        value = ''
        for token in val:
            if token["value"] in symbols:
                value += symbols[token["value"]]
            else:
                if token["type"] in ['iteration', 'option', 'group', 'or']:
                    value += token["value"]
                else:
                    for o in options:
                        if o not in list(symbols.values()):
                            symbols[token["value"]] = o
                            value += o
                            characters_extraidos[o] = token["value"].replace('"', '')
                            break

        TOKENS_RE[key] = cambio_simbolos(value)

    return TOKENS_RE

def formatear_producciones(PRODUCTIONS):
    options = ['b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

    for key, val in PRODUCTIONS.items():
        value = ''
        for token in val:
            # value += token.value
            if token["value"] in symbols:
                value += symbols[token["value"]]
            else:
                if token["type"] in ['iteration', 'option', 'group', 'or']:
                    value += token["value"]
                else: 
                    for o in options:
                        if o not in list(symbols.values()):
                            symbols[token["value"]] = o
                            value += o
                            characters_extraidos[o] = token["value"].replace('"', '')
                            break
                    # value += token.value

        PRODUCTIONS[key] = cambio_simbolos(value)


    PRODUCTIONS_PARSED = {}
    for key, production in PRODUCTIONS.items():
        variants = variantes_produccion(production)

        for variant in variants:
            PRODUCTIONS_PARSED[f'{key}{variants.index(variant)}'] = variant

    return PRODUCTIONS_PARSED

def variantes_produccion(production):
    exprs = []

    if '¦' in production or '[' in production:

        if '¦' in production:
            or_position = production.index('¦')

            open = None
            for i in production[::-1][or_position+1:]:
                if i in ['(', '«']:
                    open = i
                    break

            close = None
            for i in production[or_position+1:]:
                if i in [')', '»']:
                    close = i
                    break

            or_l_option = production[production.index(open) + 1:or_position]
            or_r_option = production[or_position + 1:production.index(close)]

            if '[' not in production:
                exprs.append(production.replace(or_l_option, '').replace('¦', '').replace('(', '').replace(')', ''))
                exprs.append(production.replace(or_r_option, '').replace('¦', '').replace('(', '').replace(')', ''))
            else:
                variant1 = production.replace(or_l_option, '').replace('¦', '').replace('(', '').replace(')', '')
                variant2 = production.replace(or_r_option, '').replace('¦', '').replace('(', '').replace(')', '')

                option1 = variant1[variant1.index('['):variant1.index(']')+1]
                exprs.append(variant1.replace(option1, ''))
                exprs.append(variant1.replace(option1, option1.replace('[', '').replace(']', '')))

                option2 = variant2[variant2.index('['):variant2.index(']')+1]
                exprs.append(variant2.replace(option2, ''))
                exprs.append(variant2.replace(option2, option2.replace('[', '').replace(']', '')))

        elif '[' in production:
            option = production[production.index('['):production.index(']')+1]
            exprs.append(production.replace(option, ''))
            exprs.append(production.replace(option, option.replace('[', '').replace(']', '')))

    else:
        exprs.append(production)

    return exprs

def generador_diccionario():
    token_index = 0
    while token_index < len(tokens):
        token = tokens[token_index]
        token_index += 1
        if token["type"] == 'space' or token["type"] == 'comment' or token["type"] == 'comment_block':
            continue
        elif token["type"] == 'KEYWORD' and token['value'] == '\\n':
            continue
        if token["value"] == 'EXCEPT':
            token_index += 2
            continue
        else:
            tokens_filtrados.append(token)

    global productions_extraidos
    productions_extraidos = {}

    global nombre_compilador
    nombre_compilador = ''

    global characters_extraidos
    characters_extraidos = {}

    global keywords_extraidos
    keywords_extraidos = {
        'NEWLINE': '\\\\n',
    }

    global tokens_expreg_extraidos
    tokens_expreg_extraidos = {}

    token_index = 0
    while token_index < len(tokens_filtrados):
        token = tokens_filtrados[token_index]
        if token["type"] == 'KEYWORD':
            if token["value"] == 'COMPILER':
                nombre_compilador = tokens_filtrados[token_index + 1]["value"]
            elif token["value"] == 'END':
                if nombre_compilador != tokens_filtrados[token_index + 1]["value"]:
                    text_area.insert(tk.INSERT, "Error sintáctico: Nombre de archivo no coincide", "\n")
            # Lee toda la seccion de Characters del cocol
            elif token["value"] == 'CHARACTERS':
                count = 0
                character_definition_tokens = []
                character_section_definitions = []
                while True:
                    # Iterate until end of characters section tokens
                    temp_token = tokens_filtrados[token_index + count + 1]

                    # final es el punto
                    if temp_token["type"] == 'final':
                        # If final token is reached, means that the characters definition is finished
                        character_section_definitions.append(character_definition_tokens)
                        character_definition_tokens = []
                    else:
                        character_definition_tokens.append(temp_token)
                    count += 1

                    # Entra a otra seccion diferente de CHARACTERS
                    if temp_token["value"] in ['KEYWORDS', 'TOKENS', 'PRODUCTIONS', 'END']:
                        token_index -= count
                        break
                token_index += count

                # Por toda la expresion antes del punto
                for definition_tokens in character_section_definitions:
                    value = ''
                    token_index_ = 0
                    while token_index_ < len(definition_tokens[2::]):
                        token = definition_tokens[2::][token_index_] #Se ignora el identificador y el =
                        # Un character siempre es un identificador = algo mas
                        # Se evalua todo lo despues del =
                        if token["type"] == 'ident':
                            if token["value"] == 'CHR':
                                # value += chr(int(definition_tokens[2::][token_index_ + 2]["value"]))
                                if int(definition_tokens[2::][token_index_ + 2]["value"]) not in [10, 13]:
                                    # value += chr(int(definition_tokens[definition_tokens.index(token) + 2]["value"]))
                                    value += chr(int(definition_tokens[2::][token_index_ + 2]["value"]))
                            else:
                                value += characters_extraidos[token["value"]]
                        elif token["type"] == 'string':
                            value += token["value"].replace('"', '')

                        token_index_ += 1

                    characters_extraidos[definition_tokens[0]["value"]] = value

            elif token["value"] == 'KEYWORDS' and tokens_filtrados[token_index + 1]["type"] != 'final':
                count = 0
                keyword_definition_tokens = []
                keyword_section_definitions = []
                while True:
                    temp_token = tokens_filtrados[token_index + count + 1]

                    if temp_token["type"] == 'final':
                        keyword_section_definitions.append(keyword_definition_tokens)
                        keyword_definition_tokens = []
                    else:
                        keyword_definition_tokens.append(temp_token)
                    count += 1

                    if temp_token["value"] in ['KEYWORDS', 'TOKENS', 'PRODUCTIONS', 'END']:
                        token_index -= count
                        break
                token_index += count

                for definition_tokens in keyword_section_definitions:
                    value = ''
                    for token in definition_tokens[2::]:
                        # No pueden haber identificadores ni char, solo string
                        if token["type"] == 'string':
                            value += token["value"].replace('"', '')

                    keywords_extraidos[definition_tokens[0]["value"]] = value

            elif token["value"] == 'TOKENS':
                count = 0
                token_re_definition_tokens = []
                token_re_section_definitions = []
                while True:
                    temp_token = tokens_filtrados[token_index + count + 1]

                    if temp_token["type"] == 'final':
                        token_re_section_definitions.append(token_re_definition_tokens)
                        token_re_definition_tokens = []
                    else:
                        token_re_definition_tokens.append(temp_token)
                    count += 1

                    if temp_token["value"] in ['TOKENS', 'IGNORE', 'PRODUCTIONS', 'END']:
                        token_index -= count
                        break
                token_index += count

                for definition_tokens in token_re_section_definitions:
                    value = []
                    for token in definition_tokens[2::]:
                        if token["type"] == 'ident':
                            if token["value"] not in ['EXCEPT', 'KEYWORDS']:
                                value.append(token)
                        elif token["type"] == 'string':
                            value.append(token)
                        elif token["type"] in ['iteration', 'option', 'group', 'or']:
                            value.append(token)

                    tokens_expreg_extraidos[definition_tokens[0]["value"]] = value

            elif token["value"] == 'IGNORE':
                count = 0
                white_space_decl_definition_tokens = []
                while True:
                    temp_token = tokens_filtrados[token_index + count + 1]

                    if temp_token["type"] == 'final':
                        break
                    else:
                        white_space_decl_definition_tokens.append(temp_token)
                    count += 1

                    if temp_token["value"] in ['IGNORE', 'PRODUCTIONS', 'END']:
                        token_index -= count
                        break
                token_index += count

                for token in white_space_decl_definition_tokens:
                    if token["value"] == '+':
                        continue
                    if token["type"] == 'ident':
                        if token["value"] == 'CHR':
                            if int(white_space_decl_definition_tokens[white_space_decl_definition_tokens.index(token) + 2]["value"]) not in [10, 13]:
                                ignore_extraidos['char_numbers'].append(int(white_space_decl_definition_tokens[white_space_decl_definition_tokens.index(token) + 2]["value"]))
                        else:
                            ignore_extraidos['strings'].append(characters_extraidos[token["value"]])
                    elif token["type"] == 'string':
                        ignore_extraidos['strings'].append(token["value"].replace('"', ''))

            elif token["value"] == 'PRODUCTIONS' and tokens_filtrados[token_index + 1]["type"] != 'final':
                count = 0
                production_definition_tokens = []
                production_section_definitions = []
                while True:
                    temp_token = tokens_filtrados[token_index + count + 1]

                    if temp_token["type"] == 'final':
                        production_section_definitions.append(production_definition_tokens)
                        production_definition_tokens = []
                    else:
                        production_definition_tokens.append(temp_token)
                    count += 1

                    if temp_token["value"] in ['PRODUCTIONS', 'END']:
                        token_index -= count
                        break
                token_index += count

                for definition_tokens in production_section_definitions:
                    expr = []
                    for token in definition_tokens[2::]:
                        if token["type"] == 'ident':
                            if token["value"] not in ['EXCEPT', 'KEYWORDS']:
                                expr.append(token)
                        elif token["type"] == 'string':
                            expr.append(token)
                        elif token["type"] in ['iteration', 'option', 'group', 'or']:
                            expr.append(token)

                    productions_extraidos[definition_tokens[0]["value"]] = expr

        token_index += 1

    characters_extraidos = formatear_characters(characters_extraidos)
    characters_extraidos[' '] = ' '

    tokens_expreg_extraidos = formatear_tokens_exp(tokens_expreg_extraidos)
    tokens_expreg_extraidos['space'] = ' '
    productions_extraidos = formatear_producciones(productions_extraidos)

# Lee archivo Cocol/R
def lecutra_cocol():
    entry_file = open(archivo1.get(), 'r')

    entry_file_lines = entry_file.readlines()
    entry_file.close()

    file_lines = entry_file_lines



    file_lines = []

    production_section = ''
    in_production_section = False
    for line in entry_file_lines:
        clean_line = line

        if 'PRODUCTIONS' in clean_line:
            in_production_section = True

        if in_production_section:
            production_section += clean_line

    cont = 0
    special_chars = []
    while cont < len(production_section):
        if production_section[cont] == '"':
            next_char = production_section[cont + 1]
            next_char_2 = production_section[cont + 2]

            if next_char_2 == '"':
                special_chars.append(next_char)
        cont += 1

    for line in entry_file_lines:
        clean_line = line

        if '//' in clean_line:
            clean_line = clean_line[:clean_line.index('//')]

        file_lines.append(clean_line.replace('\t', ' ' * 4))
        
        if 'TOKENS' in clean_line:
            for special_char in special_chars:
                if special_char == '*':
                    file_lines.append(f'multiplacion = "{special_char}".')
                elif special_char == '/':
                    file_lines.append(f'division = "{special_char}".')
                elif special_char == ';' or special_char == '.':
                    file_lines.append(f'final = "{special_char}".')
                elif special_char == '%':
                    file_lines.append(f'modulo = "{special_char}".')
                elif special_char == '^':
                    file_lines.append(f'potencia = "{special_char}".')
                # elif special_char == '(':
                #     file_lines.append(f'parentesisA = "{special_char}".')
                # elif special_char == ')':
                #     file_lines.append(f'parentesisB = "{special_char}".')
                # elif special_char == '+':
                #     file_lines.append(f'suma = "{special_char}".')
                # elif special_char == '-':
                #     file_lines.append(f'resta = "{special_char}".')
                else:
                    file_lines.append(f'{special_char} = "{special_char}".')



    # cont = 0
    # for i in entry_file_lines:
    #     cont += 1
    #     cont_com = 0
    #     cont_com2 = 0
    #     regpunto = re.search(r'[\.]$', i)

    #     if len(i) <= 3 and i != "\n":
    #         text_area.insert(tk.INSERT, f"Error en la línea {cont}: {i}")

    #     if i.count("{") != i.count("}"):
    #             text_area.insert(tk.INSERT, f"Error en la línea {cont}: no corresponden las llaves {i}")

    #     if regpunto == None and i != "\n" and cont != 1 and cont != len(entry_file_lines):
    #         if i.isupper():
    #             pass
    #         else:
    #             text_area.insert(tk.INSERT, f"Error en la línea {cont}: falta el punto. {i}")

            
    #         for char in i:
    #             if char == ")":
    #                 cont_com -= 1
    #             elif char == "(":
    #                 cont_com += 1

    #             if char == "}":
    #                 cont_com2 -= 1
    #             elif char == "{":
    #                 cont_com2 += 1

    #             if cont_com < 0:
    #                 break
    #         if cont_com2 != 0:
    #             text_area.insert(tk.INSERT, f"Error en la línea {cont}: no corresponden las llaves {i}")
    #         if cont_com != 0 or i.count('"') % 2 != 0:
    #             text_area.insert(tk.INSERT, f"Error en la línea {cont}: falta unas comillas {i}")


    # with open(archivo1.get()) as file:
    #     contents = file.read()

    #     if "EXCEPT KEYWORDS" in contents:
    #         count_word = contents.count("KEYWORDS")
    #         if count_word == 1:
    #             text_area.insert(tk.INSERT, "Erro: no existe la palabra KEYWORDS en el archivo\n")
    #             # text_area.tag_config("start", foreground="orange")
    #             # text_area.tag_add("start", "1.0", "1.52")
    #         pass
    #     if "KEYWORDS" not in contents:
    #         text_area.insert(tk.INSERT, "Error: no existe la palabra KEYWORDS en el archivo\n")
    #     if "CHARACTERS" not in contents:
    #         text_area.insert(tk.INSERT, "Error: no existe la palabra CHARACTERS en el archivo\n")
    #     if "TOKENS" not in contents:
    #         text_area.insert(tk.INSERT, "Error: no existe la palabra TOKENS en el archivo\n")
    

    line_index = 0
    while line_index < len(file_lines):
        line = file_lines[line_index].replace('\n', '\\n')
        analyzed_lines = centinela(line, line_index) # Retorna cantidad de lineas analizadas
        line_index += analyzed_lines


    for token in tokens:
        if token['type'] == 'ERROR':
            text_area.insert(tk.INSERT, f"Error en la línea  {token['line']}: {token['value']}\n")
    
def scanner():
    scanner_lineas.append("from afd import AFD")
    scanner_lineas.append("import tkinter as tk")
    scanner_lineas.append("import json")
    scanner_lineas.append("from tkinter import scrolledtext as st \n")

    scanner_lineas.append("characters = {")
    for key, value in characters_extraidos.items():
        scanner_lineas.append(f"    '{key}': '{value}',")
    scanner_lineas.append("}\n")

    scanner_lineas.append("keywords = {")
    for key, value in keywords_extraidos.items():
        scanner_lineas.append(f"    '{key}': '{value}',")
    scanner_lineas.append("}\n")

    scanner_lineas.append("tokens_expreg = {")
    for key, value in tokens_expreg_extraidos.items():
        scanner_lineas.append(f"    '{key}': '{value}',")
    scanner_lineas.append("}\n")

    scanner_lineas.append('IGNORE = {\n')
    scanner_lineas.append(f"    'char_numbers': {ignore_extraidos['char_numbers']},\n")
    scanner_lineas.append(f"    'strings': {ignore_extraidos['strings']},\n")
    scanner_lineas.append('}\n')

    scanner_lineas.append('PRODUCTIONS = {\n')
    for key, value in productions_extraidos.items():
        scanner_lineas.append(f"    '{key}': '{value}',\n")
    scanner_lineas.append('}\n')


    scanner_lineas.append("tokens = []\n")

    scanner_lineas.append("def tipo_token(word):")
    scanner_lineas.append("    if word in keywords.values():")
    scanner_lineas.append("        return 'KEYWORD'")
    scanner_lineas.append("    else:")
    scanner_lineas.append("        for token_type, re in tokens_expreg.items():")
    scanner_lineas.append("            if AFD(re.replace('a', '«««««««««««««««««l¦d»¦s»¦o»¦ »¦(»¦)»¦/»¦*»¦=»¦.»¦|»¦[»¦]»¦{»¦}»¦<»¦>»')).accepts(word, characters):")
    scanner_lineas.append("                return token_type")
    scanner_lineas.append("    return 'ERROR'\n")


    scanner_lineas.append("def centinela(entry_file_lines, line, line_index):")
    scanner_lineas.append("    analyzed_lines = 1")
    scanner_lineas.append("    line_position = 0")
    scanner_lineas.append("    current_line_recognized_tokens = []")
    scanner_lineas.append("    while line_position < len(line):")
    scanner_lineas.append("        current_token = None")
    scanner_lineas.append("        next_token = None")
    scanner_lineas.append("        avance = 0")
    scanner_lineas.append("        continuar = True")
    scanner_lineas.append("        while continuar:")
    scanner_lineas.append("            if current_token and next_token:")
    scanner_lineas.append("                if current_token['type'] != 'ERROR' and next_token['type'] == 'ERROR':")
    scanner_lineas.append("                    avance -= 1")
    scanner_lineas.append("                    continuar = False")
    scanner_lineas.append("                    break\n")

    scanner_lineas.append("            if line_position + avance > len(line):")
    scanner_lineas.append("                continuar = False")
    scanner_lineas.append("                break\n")

    scanner_lineas.append("            if line_position + avance <= len(line):")
    scanner_lineas.append("                current_token = {")
    scanner_lineas.append("                    'type': tipo_token(line[line_position:line_position + avance]),")
    scanner_lineas.append("                    'value': line[line_position:line_position + avance],")
    scanner_lineas.append("                    'line': line_index")
    scanner_lineas.append("                }")

    scanner_lineas.append("            avance += 1\n")

    scanner_lineas.append("            if line_position + avance <= len(line):")
    scanner_lineas.append("                next_token = {")
    scanner_lineas.append("                    'type': tipo_token(line[line_position:line_position + avance]),")
    scanner_lineas.append("                    'value': line[line_position:line_position + avance],")
    scanner_lineas.append("                    'line': line_index")
    scanner_lineas.append("                }")

    scanner_lineas.append("        line_position = line_position + avance\n\n")


    scanner_lineas.append("        if current_token and current_token['type'] != 'ERROR':")
    scanner_lineas.append("            tokens.append(current_token)")
    scanner_lineas.append("            current_line_recognized_tokens.append(current_token)")

    scanner_lineas.append("            if line_position == len(line) + 1 and len(current_line_recognized_tokens) != 0:")
    scanner_lineas.append("                tokens.append(current_token)\n")

    scanner_lineas.append("            if line_position == len(line) + 1 and len(current_line_recognized_tokens) == 0:")
    scanner_lineas.append("                if line_index < len(entry_file_lines) - 1:")
    scanner_lineas.append("                    new_line = line + ' ' + entry_file_lines[line_index + 1].replace('\\n', '\\\\n')")
    scanner_lineas.append("                    line_index += 1")
    scanner_lineas.append("                    analyzed_lines += centinela(entry_file_lines, new_line, line_index)\n")

    scanner_lineas.append("    return analyzed_lines\n")


    scanner_lineas.append(f"entry_file = open('{archivo2.get()}', 'r')")

    scanner_lineas.append("entry_file_lines = entry_file.readlines()")
    scanner_lineas.append("entry_file.close()\n")

    scanner_lineas.append("line_index = 0")
    scanner_lineas.append("while line_index < len(entry_file_lines):")
    scanner_lineas.append("    line = entry_file_lines[line_index].replace('\\n', '\\\\n')")
    scanner_lineas.append("    analyzed_lines = centinela(entry_file_lines, line, line_index)")
    scanner_lineas.append("    line_index += analyzed_lines\n")


    scanner_lineas.append("for token in tokens:")
    scanner_lineas.append("    if token['type'] == 'ERROR':")
    scanner_lineas.append("        print(f'Lexical error on line {token[\"line\"]}: {token[\"value\"]}')")


    # Se muestran los tokens en una nueva ventana
    scanner_lineas.append("window = tk.Tk()")
    scanner_lineas.append("window.title('Tokens')")
    scanner_lineas.append("window.geometry('500x250')  ")
    scanner_lineas.append("text_area = st.ScrolledText(window, width = 60, height = 15, font = ('Times New Roman',15), foreground = 'white')")
    scanner_lineas.append("text_area.grid(column = 1, row = 1, columnspan=2)")

    # scanner_lineas.append("instruction = []") 
    scanner_lineas.append("for token in tokens:")
    scanner_lineas.append("    if token['type'] == 'IGNORE':")
    scanner_lineas.append("        continue")
    scanner_lineas.append("    if token['type'] == 'KEYWORD':")
    scanner_lineas.append("        if token['value'] == '\\\\n':")
    scanner_lineas.append("            text_area.insert(tk.INSERT, '\\n')")
    scanner_lineas.append("        else:")
    scanner_lineas.append("            text_area.insert(tk.INSERT, f'{token[\"value\"]} ', " ")")
    # scanner_lineas.append("            instruction.append({")
    # scanner_lineas.append("                'type': token['type'],")
    # scanner_lineas.append("                'value': token['value'],")
    # scanner_lineas.append("            })")
    scanner_lineas.append("    elif token['type'] == 'space':")
    scanner_lineas.append("        continue")
    scanner_lineas.append("    else:")
    scanner_lineas.append("        text_area.insert(tk.INSERT, f'{token[\"type\"]} ')")
    # scanner_lineas.append("        instruction.append({")
    # scanner_lineas.append("            'type': token['type'],")
    # scanner_lineas.append("            'value': token['value'],")
    # scanner_lineas.append("        })")

    scanner_lineas.append("window.mainloop()")

    scanner_lineas.append("instruction = []")
    scanner_lineas.append("for token in tokens:")
    scanner_lineas.append("    if token['type'] == 'IGNORE':")
    scanner_lineas.append("        continue")
    scanner_lineas.append("    if token['type'] == 'KEYWORD':")
    scanner_lineas.append("        if token['value'] == '\\\\n':")
    scanner_lineas.append("            continue")
    scanner_lineas.append("        else:")
    scanner_lineas.append("            instruction.append({")
    scanner_lineas.append("                'type': token['type'],")
    scanner_lineas.append("                'value': token['value'],")
    scanner_lineas.append("            })")
    scanner_lineas.append("    elif token['type'] == 'space':")
    scanner_lineas.append("        continue")
    scanner_lineas.append("    else:")
    scanner_lineas.append("        instruction.append({")
    scanner_lineas.append("            'type': token['type'],")
    scanner_lineas.append("            'value': token['value'],")
    scanner_lineas.append("        })")

    scanner_lineas.append("with open('tokens.txt', 'w', encoding='utf-8') as file:")
    scanner_lineas.append("    json.dump(instruction, file, ensure_ascii = False, indent = 4)")

    lex_analyzer = open('scanner.py', 'w+')

    for line in scanner_lineas:
        lex_analyzer.write(line)
        lex_analyzer.write("\n")

def ejecutar_scanner():
    ejecutar_archivo_scanner.set(True)
    button_run_script.grid_forget()
    os.system('pipenv run python3 scanner.py')

def ejecutar_parser():
    ejecutar_archivo_parser.set(True)
    button_run_parser.grid_forget()
    os.system('pipenv run python3 parser.py')

def no_terminales_indice():
    for k, v in productions_extraidos.items():
        nonTerminal = k
        if nonTerminal not in noTerminalesNumber:
            noTerminalesNumber.append(nonTerminal)

def no_terminales():
    for k, v in productions_extraidos.items():
        nonTerminal = k[:-1]
        if nonTerminal not in noTerminales:
            noTerminales.append(nonTerminal)

def primero(produccion, primeros = []):
    if produccion not in noTerminalesNumber:
        if produccion not in primeros:
            primeros.append(produccion)
    else:
        for k, prod in productions_extraidos.items():
            string_production = productions_extraidos[produccion].replace('«', '').replace('»', '').replace('±', '')
            if characters_extraidos[string_production[0]] in k:
                primero(k, primeros)
            elif characters_extraidos[string_production[0]] not in noTerminales:
                primero(characters_extraidos[string_production[0]], primeros)

    return primeros

def producciones():
    production_tokens = []


    in_production_tokens = False
    for token in tokens_filtrados:
        if token["value"] == 'PRODUCTIONS':
            in_production_tokens = True
            continue
        elif token["value"] == 'END':
            in_production_tokens = False
            continue

        if in_production_tokens:
            if token["type"] == 'ident' and tokens_expreg_extraidos.get(token["value"]):
                temp_token = {**token, 'type': 'token'}
                production_tokens.append(temp_token)
                continue

            production_tokens.append(token)

    return production_tokens

def metodos_parser():
    parser_file_lines = []
    production_tokens = producciones() 

    starting_production = True
    tabs = 0
    on_if = False
    current_def = None
    for token in production_tokens:
        if starting_production:
            next_token = production_tokens[production_tokens.index(token) + 1]
            tabs = 1
            current_def = token["value"]
            if next_token["type"] == 'attrs':
                ref = next_token["value"].replace('<.', '').replace('.>', '').replace('ref', '').strip()
                tabs_str = '    ' * tabs
                parser_file_lines.append(f'{tabs_str}def {token["value"]}(self, {ref}):\n')
            else:
                tabs_str = '    ' * tabs
                parser_file_lines.append(f'{tabs_str}def {token["value"]}(self):\n')
            tabs = 2

        if token["type"] == 'iteration':
            if current_def == 'EstadoInicial':
                while_condition = f"self.current_token['type'] in {primero('EstadoInicial0')}"
            else:
                strings_in_iteration = []
                for t in production_tokens[production_tokens.index(token) + 1:]:
                    if t["type"] == 'string':
                        strings_in_iteration.append(t["value"].replace('"', ''))
                    elif t["value"] == '}':
                        break

                while_condition = f"self.current_token['value'] in {strings_in_iteration}"

            if token["value"] == '{':
                tabs_str = '    ' * tabs
                parser_file_lines.append(f'{tabs_str}while {while_condition}:\n')
                tabs += 1
            elif token["value"] == '}':
                tabs -= 1

        if token["type"] == 'semantic_action':
            action = token["value"].replace('(.', '').replace('.)', '').strip()
            if 'return' in action and on_if:
                tabs -= 1
                parser_file_lines.append('\n')
            tabs_str = '    ' * tabs
            parser_file_lines.append(f'{tabs_str}{action}\n')

        if token["type"] == 'ident' and not starting_production:
            next_token = production_tokens[production_tokens.index(token) + 1]
            
            if next_token["type"] == 'attrs':
                ref = next_token["value"].replace('<.', '').replace('.>', '').replace('ref', '').strip()
                tabs_str = '    ' * tabs
                parser_file_lines.append(f'{tabs_str}{ref} = self.{token["value"]}({ref})\n')
            else:
                tabs_str = '    ' * tabs
                parser_file_lines.append(f'{tabs_str}self.{token["value"]}()\n')

        if token["type"] == 'token':
            tabs_str = '    ' * tabs
            parser_file_lines.append(f'{tabs_str}{token["value"]} = None\n')
            parser_file_lines.append(f'{tabs_str}if self.current_token["type"] == "{token["value"]}":\n')
            tabs += 1
            tabs_str = '    ' * tabs
            parser_file_lines.append(f'{tabs_str}{token["value"]} = float(self.current_token["value"])\n')
            parser_file_lines.append(f'{tabs_str}self.update_current_token()\n')
            tabs -= 1

        if token["type"] == 'string':
            if token["value"] != '")"':
                if on_if:
                    tabs -= 1

                on_if = True
                parser_file_lines.append('\n')
                tabs_str = '    ' * tabs
                parser_file_lines.append(f'{tabs_str}if self.current_token["value"] == {token["value"]}:\n')
                tabs += 1
            tabs_str = '    ' * tabs
            parser_file_lines.append(f'{tabs_str}self.update_current_token()\n')

        if token["type"] == 'option' and token["value"] == ']':
            on_if = False
            tabs -= 1
            parser_file_lines.append('\n')

        if token["type"] == 'final':
            tabs = 0
            on_if = False
            parser_file_lines.append('\n')
            starting_production = True
        else:
            starting_production = False

    parser(parser_file_lines)

def parser(metodos):
    parser_class_header = [
        'import tkinter as tk\n'
        'from tkinter import scrolledtext as st\n\n'


        'window = tk.Tk()\n',
        'window.title("Resultado")\n',
        'window.geometry("500x250")\n',
        'text_area = st.ScrolledText(window, width = 60, height = 15, font = ("Times New Roman",15), foreground = "white")\n',
        'text_area.grid(column = 1, row = 1, columnspan=2)\n',

        'class Parser():\n',
        '    def __init__(self, tokens):\n',
        '        self.tokens = tokens\n',
        '        self.current_token_index = 0\n',
        '        self.current_token = self.tokens[self.current_token_index]\n',
        '        self.EstadoInicial()\n\n',
        
        '    def update_current_token(self):\n',
        '        if self.current_token_index < len(self.tokens) - 1:\n',
        '            self.current_token_index += 1\n',
        '            self.current_token = self.tokens[self.current_token_index]\n\n',
        
    ]

    with open('tokens.txt', 'r') as file:
        instruction_json = json.load(file)

    class_init = [
        f'Parser({instruction_json})\n',
        'window.mainloop()'
    ]

    with open('parser.py', 'w') as file:
        file.writelines(parser_class_header)
        file.writelines(metodos)
        file.writelines(class_init)

window = tk.Tk()

archivo1 = tk.StringVar()
archivo2 = tk.StringVar()

window.title('Analizador Lexico')
window.geometry("500x500")  
# window.config(background = "white")

# Archivo 1
label_file_explorer = tk.Label(window, text = "Seleccione un archivo", width = 20, height = 4, fg = "white")
button_explore = tk.Button(window, text = "Seleccionar archivo", command = browseFiles)

# Archivo 2
label_file_explorer2 = tk.Label(window, text = "Seleccione un archivo", width = 20, height = 4, fg = "white")
button_explore2 = tk.Button(window, text = "Seleccionar archivo", command = browseFiles2)

# Errores
text_area = st.ScrolledText(window, width = 60, height = 8, font = ("Times New Roman",15), foreground = "red")

creador = tk.Label(window, text="Por Gian Luca Rivera", pady=50, anchor="e", justify=CENTER)
progress = ttk.Progressbar(window, orient = HORIZONTAL,length = 100, mode = 'determinate')
  
label_file_explorer.grid(column = 1, row = 1)  
button_explore.grid(column = 2, row = 1)
label_file_explorer2.grid(column = 1, row = 2)  
button_explore2.grid(column = 2, row = 2)
text_area.grid(column = 1, row = 3, columnspan=2)
# text_area.configure(state ='disabled')
creador.grid(column = 1,row = 4, columnspan=2)

# Espera que se suban archivos para continuar
button_explore.wait_variable(archivo1)
button_explore2.wait_variable(archivo2)

creador.grid_forget()
progress.grid(column = 1,row = 4, columnspan=2)
creador.grid(column = 1,row = 5, columnspan=2)

step()

step()
lecutra_cocol()

step()
generador_diccionario()

step()
scanner()

step()
ejecutar_archivo_scanner = tk.BooleanVar()
button_run_script = tk.Button(window, text = "Ejecutar scanner", command = ejecutar_scanner)
progress.grid_forget()
button_run_script.grid(column = 1, row = 4, columnspan=2)
creador.grid(column = 1,row = 5, columnspan=2)
button_run_script.wait_variable(ejecutar_archivo_scanner)


# Despues de correr scanner
no_terminales_indice()
no_terminales()
primero('EstadoInicial0')
metodos_parser()
button_run_script.grid_forget()
creador.grid_forget()
ejecutar_archivo_parser = tk.BooleanVar()
button_run_parser = tk.Button(window, text="Ejecutar parser", command= ejecutar_parser)
button_run_parser.grid(column = 1, row = 4, columnspan=2)
window.title('Analizador Sintáctico')
button_run_parser.wait_variable(ejecutar_archivo_parser)

answer = mb.askyesno(message="Analizador lexico ejecutado con éxito!\n\n¿Deseas continuar con otro analizador?", title="Ejecución finalizada")
if answer:
    python = sys.executable
    os.execl(python, python, * sys.argv)
else:
    window.destroy()


window.mainloop()