import os

import lldb
from lldb import SBDebugger, SBTarget, SBProcess, SBError, SBBreakpoint


def test_create_debugger():
    debugger = SBDebugger.Create()
    assert debugger is not None


def test_create_target(executable):
    debugger: SBDebugger = SBDebugger.Create()
    target: SBTarget = debugger.CreateTargetWithFileAndArch(executable, lldb.LLDB_ARCH_DEFAULT)

    assert target is not None


def test_launch_process(executable):
    debugger: SBDebugger = SBDebugger.Create()
    target: SBTarget = debugger.CreateTargetWithFileAndArch(executable, lldb.LLDB_ARCH_DEFAULT)
    error = SBError()
    process: SBProcess = target.Launch(debugger.GetListener(), None, None,
                                        None, None, None,
                                        None, 0, False, error)

    assert error.success, error.description
    assert process is not None
    assert process.id != 0


def test_launch_process_with_breakpoint(executable):
    debugger: SBDebugger = SBDebugger.Create()
    debugger.SetAsync(False)
    target: SBTarget = debugger.CreateTargetWithFileAndArch(executable, lldb.LLDB_ARCH_DEFAULT)
    bp: SBBreakpoint = target.BreakpointCreateByName("main", target.GetExecutable().GetFilename())
    assert bp is not None
    process: SBProcess = target.LaunchSimple(None, None, os.getcwd())
    assert process.is_stopped
    assert process.id != 0
    process.Continue()
