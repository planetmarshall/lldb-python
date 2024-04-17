lldb-python
===========

An unofficial self contained distribution of the 
[LLDB Python API](https://lldb.llvm.org/python_api.html) to ease integration of the
LLDB debugger into external Python projects.

The Python API is normally distributed as part of the main LLDB package, but this
typically uses the System Python which can make it difficult to integrate into
standalone Python projects that typically will use a virtual environment

Installation
------------

Download the appropriate wheel file for your platform and architecture and install
using PIP.

Example Usage
-------------

There are extensive examples in the [LLDB Documentation](https://lldb.llvm.org/use/python.html)
and the [LLVM Repository](https://github.com/llvm/llvm-project/tree/main/lldb/examples/python)

There is also a basic test suite in the `test` folder of this repository


Build
-----

Wheels are built using [scikit-build-core](https://github.com/scikit-build/scikit-build-core)
and [cibuildwheel](https://github.com/pypa/cibuildwheel). Some post-build customization
of the built wheel is done that could not be accomplished using these tools alone.

```
./download-llvm.sh
pipx run build -v --wheel
./edit-wheel.sh
```

Then to test the wheel
```
pip install -r requirements.txt
python -m venv .venv
source .venv/bin/activate
pip install dist/<wheel_file>
pytest -v test
```
