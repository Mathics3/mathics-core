"""
Default Mathics3 Interrupt routines.

Note: other environments may build on or use other interrupt handlers
"""

import signal
import subprocess
import sys
from types import FrameType
from typing import Callable, Optional

from mathics import settings
from mathics.core.evaluation import Evaluation
from mathics.core.interrupt import AbortInterrupt, ReturnInterrupt, TimeoutInterrupt
from mathics.eval.stackframe import find_Mathics3_evaluation_method, get_eval_Expression


# See also __main__'s interactive_eval_loop
def inspect_eval_loop(evaluation: Evaluation):
    """
    A read eval/loop for an Interrupt's "inspect" command.
    """
    shell = evaluation.shell
    if shell is not None:
        was_inside_interrupt = shell.is_inside_interrupt
        shell.is_inside_interrupt = True
    else:
        was_inside_interrupt = False

    previous_recursion_depth = evaluation.recursion_depth
    while True:
        try:
            # Reset line number within an In[] line number.
            # Note: this is not setting as, say, In[5]
            # to back to In[1], but instead it sets the line number position *within*
            # In[5]. The user input for "In[5]" might have several continuation lines.
            if shell is not None and hasattr(shell, "lineno"):
                shell.lineno = 0

            query, source_code = evaluation.parse_feeder_returning_code(shell)
            # show_echo(source_code, evaluation)
            if len(source_code) and source_code[0] == "!" and shell is not None:
                subprocess.run(source_code[1:], shell=True)
                if shell.definitions is not None:
                    shell.definitions.increment_line_no(1)
                continue
            if query is None:
                continue
            result = evaluation.evaluate(query, timeout=settings.TIMEOUT)
            if result is not None and shell is not None:
                shell.print_result(result, strict_wl_output=True)
        except TimeoutInterrupt:
            print("\nTimeout occurred - ignored.")
            pass
        except ReturnInterrupt:
            evaluation.last_eval = None
            evaluation.exc_result = None
            evaluation.message("Interrupt", "dgend")
            raise
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")
        except EOFError:
            print()
            raise
        except SystemExit:
            # raise to pass the error code on, e.g. Quit[1]
            raise
        finally:
            evaluation.recursion_depth = previous_recursion_depth
            if shell is not None:
                shell.is_inside_interrupt = was_inside_interrupt


def Mathics3_interrupt_handler(
    evaluation: Optional[Evaluation], interrupted_frame: FrameType, print_fn: Callable
):
    try:
        import readline  # noqa
    except ImportError:
        pass

    while True:
        try:
            user_input = input("interrupt> ").strip()
            if user_input in ("a", "abort"):
                print_fn("aborting")
                raise AbortInterrupt
            elif user_input in ("continue", "c"):
                print_fn("continuing")
                break
            elif user_input in ("debugger", "d"):
                breakpoint()
            elif user_input in ("exit", "quit"):
                print_fn("Mathics3 exited because of an interrupt.")
                sys.exit(3)
            elif user_input in ("inspect", "i"):
                print_fn("inspecting")
                if evaluation is not None:
                    evaluation.message("Interrupt", "dgbgn")
                    inspect_eval_loop(evaluation)

            elif user_input in ("show", "s"):
                # In some cases we can better, by going back to the caller
                # and reconstructing the actual call with arguments.
                eval_frame = find_Mathics3_evaluation_method(interrupted_frame)
                if eval_frame is None:
                    continue
                eval_method_name = eval_frame.f_code.co_name
                eval_method = getattr(eval_frame.f_locals.get("self"), eval_method_name)
                if eval_method:
                    print_fn(eval_method.__doc__)
                eval_expression = get_eval_Expression()
                if eval_expression is not None:
                    print_fn(str(eval_expression))
                break
            elif user_input in ("trace", "t"):
                print_fn("tracing")
            else:
                print_fn(
                    """Your options are:
	abort (or a) to abort current calculation
	continue (or c) to continue
	debugger (or d) to to enter a Python debugger
	exit (or quit) to exit Mathics3
	inspect (or i) to enter an interactive dialog
	show (or s) to show current operation (and then continue)
"""
                )
        except KeyboardInterrupt:
            print_fn("\nKeyboardInterrupt")
        except EOFError:
            print_fn("")
            break
        except TimeoutInterrupt:
            # There might have been a Pause[] set before we entered
            # this handler. If that happens, we can clear the
            # error. Ideally the interrupt REPL would would have clear
            # all timeout signals, but Python doesn't support that, as
            # far as I know.
            #
            # Here, we note we have time'd out. This also silences
            # other handlers that we've handled this.
            if evaluation is not None:
                evaluation.timeout = True
            break
        except ReturnInterrupt:
            # the interrupt shell probably isssued a Return[].
            # Respect that.
            break
        except RuntimeError:
            break
        finally:
            pass


def Mathics3_basic_signal_handler(sig, interrupted_frame):
    """
    Custom signal handler for SIGINT (Ctrl+C).
    """
    evaluation: Optional[Evaluation] = None
    # Find an evaluation object to pass to the Mathics3 interrupt handler
    while interrupted_frame is not None:
        if (
            evaluation := interrupted_frame.f_locals.get("evaluation")
        ) is not None and isinstance(evaluation, Evaluation):
            break
        interrupted_frame = interrupted_frame.f_back
    print_fn = evaluation.print_out if evaluation is not None else print
    print_fn("")
    if interrupted_frame is None:
        print("Unable to find Evaluation frame to start on")
    Mathics3_interrupt_handler(evaluation, interrupted_frame, print_fn)


def setup_signal_handler():
    signal.signal(signal.SIGINT, Mathics3_basic_signal_handler)
