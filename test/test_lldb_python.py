import lldb
from lldb import SBDebugger, SBTarget, SBProcess, SBError, SBBreakpoint


def _launch_process(target: SBTarget) -> SBProcess:
    error = SBError()
    process: SBProcess = target.Launch(target.debugger.GetListener(), None, None,
                                        None, None, None,
                                        None, 0, False, error)
    assert error.success, error.description
    return process


def test_create_debugger(debugger):
    assert debugger is not None


def test_create_target(debugger, executable):
    target: SBTarget = debugger.CreateTargetWithFileAndArch(executable, lldb.LLDB_ARCH_DEFAULT)

    assert target is not None


def test_launch_process(debugger, executable):
    target: SBTarget = debugger.CreateTargetWithFileAndArch(executable, lldb.LLDB_ARCH_DEFAULT)
    process: SBProcess = _launch_process(target)

    assert process is not None
    assert process.id != 0


def test_launch_process_with_breakpoint(debugger, executable):
    debugger.SetAsync(False)
    target: SBTarget = debugger.CreateTargetWithFileAndArch(executable, lldb.LLDB_ARCH_DEFAULT)
    bp: SBBreakpoint = target.BreakpointCreateByName("main", target.GetExecutable().GetFilename())

    assert bp is not None
    assert bp.num_locations == 1
    process: SBProcess = _launch_process(target)

    assert process.is_stopped

    process.Continue()
