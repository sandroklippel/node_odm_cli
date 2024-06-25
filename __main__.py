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

""" Command line interface for NodeODM
"""

import os
import sys
import json
import argparse
from datetime import timedelta
from tqdm import tqdm
from pyodm import Node
from pyodm.exceptions import NodeConnectionError, NodeResponseError, TaskFailedError

__author__ = "Sandro Klippel"
__copyright__ = "Copyright 2024, Sandro Klippel"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Sandro Klippel"
__email__ = "sandroklippel at gmail.com"
__status__ = "Prototype"
__revision__ = "$Format:%H$"

DEFAULT_OPTIONS = {"auto-boundary": True}
DEFAULT_REFRESH = 30  # seconds


class ProgressBar(tqdm):

    def set(self, n):
        self.n = n
        self.refresh()


def fmt_elapsed_time(ms):
    td = timedelta(milliseconds=ms)
    if td.days > 0:
        return f"{td.days}d {td.seconds // 3600}h {td.seconds % 3600 // 60}m {td.seconds % 60}s"
    elif td.seconds >= 3600:
        return f"{td.seconds // 3600}h {td.seconds % 3600 // 60}m {td.seconds % 60}s"
    elif td.seconds >= 60:
        return f"{td.seconds // 60}m {td.seconds % 60}s"
    else:
        return f"{td.seconds}s {td.microseconds // 1000}ms"


def read_options(s):
    if s is not None and os.path.isfile(s):
        with open(s, "r") as jsonfile:
            try:
                opt = json.load(jsonfile)
            except json.JSONDecodeError:
                print(
                    "Error: invalid preset file, using default options", file=sys.stderr
                )
                opt = DEFAULT_OPTIONS
        return opt
    elif isinstance(s, str):
        try:
            opt = json.loads(s)
        except json.JSONDecodeError:
            print("Error: invalid settings, using defaults", file=sys.stderr)
            opt = DEFAULT_OPTIONS
        return opt
    else:
        return DEFAULT_OPTIONS


def is_valid_output_dir(output_dir):
    if not os.path.isabs(output_dir):
        return False  # O caminho não é absoluto

    parent_dir = os.path.dirname(output_dir)
    if not os.access(parent_dir, os.W_OK):
        return False  # Sem permissão de escrita no diretório pai

    if os.path.isfile(output_dir):
        return False  # O caminho especificado é um arquivo e não um diretório

    return True


def lista_arquivos_jpg(diretorio):
    """Retorna uma lista de arquivos JPG em um diretório, com caminhos relativos."""

    arquivos_jpg = []
    for nome_arquivo in os.listdir(diretorio):
        caminho_completo = os.path.join(diretorio, nome_arquivo)
        if os.path.isfile(caminho_completo) and nome_arquivo.lower().endswith(".jpg"):
            arquivos_jpg.append(os.path.relpath(caminho_completo, start=os.curdir))
    return arquivos_jpg


def cli():
    """command line interface"""
    parser = argparse.ArgumentParser(
        description="Command line interface for NodeODM", epilog=__copyright__
    )
    parser.add_argument("folder", help="Photo folder")
    parser.add_argument(
        "-s",
        "--server",
        dest="server",
        default="localhost",
        type=str,
        help="Hostname or IP address of processing node",
    )
    parser.add_argument(
        "-p",
        "--port",
        dest="port",
        default="3000",
        type=int,
        help="Port of processing node",
    )
    parser.add_argument(
        "-t",
        "--token",
        dest="token",
        default="",
        type=str,
        help="Token to use for authentication",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="outdir",
        type=str,
        help="Absolute path to save output files (defaults to photo folder)",
    )
    parser.add_argument(
        "--name", dest="taskname", type=str, help="User-friendly name for the task"
    )
    parser.add_argument(
        "--timeout",
        dest="timeout",
        default=30,
        type=int,
        help="Timeout value in seconds for network requests",
    )
    parser.add_argument(
        "--options",
        dest="options",
        type=str,
        help="Task' settings (preset filename or json string)",
    )
    parser.add_argument("--version", action="version", version=__version__)

    args = parser.parse_args()

    if os.path.isdir(args.folder):
        arquivos_jpg = lista_arquivos_jpg(args.folder)
        task_name = (
            os.path.basename(args.folder) if args.taskname is None else args.taskname
        )
    else:
        print("Error: invalid photo folder", file=sys.stderr)
        return 1

    if not arquivos_jpg:
        print("Error: no input files", file=sys.stderr)
        return 1

    if args.outdir is not None and is_valid_output_dir(args.outdir):
        outdir = args.outdir
    else:
        outdir = os.path.abspath(args.folder)

    task_options = read_options(args.options)

    node = Node(
        host=args.server, port=args.port, token=args.token, timeout=args.timeout
    )

    try:
        # Start a task
        with ProgressBar(
            total=100.0,
            unit="%",
            desc="Uploading images.......",
            initial=0,
            ascii=True,
            smoothing=1,
            bar_format="{l_bar}{bar}",
            file=sys.stdout,
        ) as pb:
            task = node.create_task(
                files=arquivos_jpg,
                name=task_name,
                options=task_options,
                progress_callback=lambda x: pb.set(round(x, 2)),
            )

        info = task.info()
        print("Task unique identifier.: {}".format(info.uuid))
        print("Number of images.......: {}".format(info.images_count))

        try:

            # This will block until the task is finished processing
            # or will raise an exception
            with ProgressBar(
                total=100.0,
                unit="%",
                desc="Processing.............",
                initial=0,
                ascii=True,
                smoothing=1,
                bar_format="{l_bar}{bar}",
                file=sys.stdout,
            ) as pb:
                task.wait_for_completion(
                    status_callback=lambda x: pb.set(round(x.progress, 2)),
                    interval=DEFAULT_REFRESH,
                )

            info = task.info()
            print(
                "Task <{}> completed in {}".format(
                    info.name, fmt_elapsed_time(info.processing_time)
                )
            )

            # Retrieve results
            with ProgressBar(
                total=100.0,
                unit="%",
                desc="Downloading results....",
                initial=0,
                ascii=True,
                smoothing=1,
                bar_format="{l_bar}{bar}",
                file=sys.stdout,
            ) as pb:
                task.download_assets(
                    destination=outdir, progress_callback=lambda x: pb.set(round(x, 2))
                )

            print("Assets saved in {}".format(outdir))

        except TaskFailedError as e:
            print("Task Error: {}".format(e), file=sys.stderr)
            print("\n".join(task.output(line=-10)), file=sys.stderr)
            return 1

        except KeyboardInterrupt:
            task.cancel()
            print("Task Canceled", file=sys.stderr)
            return 1

    except NodeConnectionError as e:
        print("Cannot connect: {}".format(e), file=sys.stderr)
        return 1

    except NodeResponseError as e:
        print("Error: {}".format(e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(cli())
