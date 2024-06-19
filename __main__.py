#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# MIT License

# Copyright (c) 2024 Sandro Klippel

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Interface and command line for NodeODM
"""

import os
import sys
import argparse
from pyodm import Node

__author__ = "Sandro Klippel"
__copyright__ = "Copyright 2024, Sandro Klippel"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Sandro Klippel"
__email__ = "sandroklippel at gmail.com"
__status__ = "Prototype"
__revision__ = '$Format:%H$'

def listar_arquivos_jpg(diretorio):
    """Retorna uma lista de arquivos JPG em um diretório, com caminhos relativos."""

    arquivos_jpg = []
    for nome_arquivo in os.listdir(diretorio):
        caminho_completo = os.path.join(diretorio, nome_arquivo)
        if os.path.isfile(caminho_completo) and nome_arquivo.lower().endswith(".jpg"):
            arquivos_jpg.append(os.path.relpath(caminho_completo, start=os.curdir))
    return arquivos_jpg

def cli():
    """ command line interface
    """
    parser = argparse.ArgumentParser(description="Interface e linha de comando para NodeODM.")
    parser.add_argument("diretorio", help="Diretório com as fotos")
    args = parser.parse_args()

    arquivos_jpg = listar_arquivos_jpg(args.diretorio)
    task_name = os.path.basename(args.diretorio)

    # n = Node.from_url("http://10.1.25.73:3000/?token=e3ba-4404-80d3")
    # t = n.create_task(arquivos_jpg, {"auto-boundary": True, "optimize-disk-space": True})
    n = Node("http://10.1.25.73",3001)
    t = n.create_task(arquivos_jpg, 
                      options={"max-concurrency": 16, "remove-ortho-tiles": True, "camera-cloud": True},
                      name=task_name)
    
    info = t.info()

    print('Tarefa: {}'.format(task_name))
    print('Número de imagens: {}'.format(info.images_count))
    print(info.status)

if __name__ == "__main__":
    sys.exit(cli())