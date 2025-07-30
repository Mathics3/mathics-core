"""
Default Mathics3 Interrupt routines.

Note: other environments may build on or use other interrupt handlers
"""

import inspect
import signal
import subprocess
import sys
from typing import Optional

from mathics import settings
from mathics.core.evaluation import Evaluation
from mathics.core.interrupt import AbortInterrupt, ReturnInterrupt, TimeoutInterrupt
from mathics.eval.stack import find_mathics3_evaluation_method


# See also __main__'s interactive_eval_loop
def inspect_eval_loop(evaluation: Evaluation):
    """
    A read eval/loop for an Interrupt's "inspect" command.
    """
    shell = evaluation.shell
    was_inside_interrupt = shell.is_inside_interrupt
    shell.is_inside_interrupt = True
    previous_recursion_depth = evaluation.recursion_depth
    while True:
        try:
            query, source_code = evaluation.parse_feeder_returning_code(shell)
            # show_echo(source_code, evaluation)
            if len(source_code) and source_code[0] == "!":
                subprocess.run(source_code[1:], shell=True)
                shell.definitions.increment_line_no(1)
                continue
            if query is None:
                continue
            result = evaluation.evaluate(query, timeout=settings.TIMEOUT)
            if result is not None:
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
            shell.is_inside_interrupt = was_inside_interrupt


def mathics3_interrupt_handler(evaluation: Optional[Evaluation]):
    try:
        import readline  # noqa
    except ImportError:
        pass

    while True:
        try:
            user_input = input("interrupt> ").strip()
            if user_input in ("a", "abort"):
                print("aborting")
                raise AbortInterrupt
            elif user_input in ("continue", "c"):
                print("continuing")
                break
            elif user_input in ("exit", "quit"):
                print("Mathics3 exited because of an interrupt.")
                sys.exit(3)
            elif user_input in ("inspect", "i"):
                print("inspecting")
                if evaluation is not None:
                    evaluation.message("Interrupt", "dgbgn")
                inspect_eval_loop(evaluation)

            elif user_input in ("show", "s"):
                # In some cases we can better, by going back to the caller
                # and reconstructing the actual call with arguments.
                eval_frame = find_mathics3_evaluation_method(inspect.currentframe())
                eval_method_name = eval_frame.f_code.co_name
                eval_method = getattr(eval_frame.f_locals.get("self"), eval_method_name)
                if eval_method:
                    print(eval_method.__doc__)
                else:
                    print(eval_frame)
                break
            elif user_input in ("trace", "t"):
                print("tracing")
            else:
                print(
                    """Your options are:
	abort (or a) to abort current calculation
	continue (or c) to continue
	exit (or quit) to exit Mathics3
	inspect (or i) to enter an interactive dialog
	show (or s) to show current operation (and then continue"
	trace (or t) to show all operations"
"""
                )
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")
        except EOFError:
            print()
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


def mathics3_basic_signal_handler(sig, frame):
    """
    Custom signal handler for SIGINT (Ctrl+C).
    """
    current_frame = inspect.currentframe()
    evaluation: Optional[Evaluation] = None
    # Find an evaluation object to pass to the Mathics3 interrupt handler
    while current_frame.f_back is not None:
        current_frame = current_frame.f_back
        if (
            evaluation := current_frame.f_locals.get("evaluation")
        ) is not None and isinstance(evaluation, Evaluation):
            break
    print()
    mathics3_interrupt_handler(evaluation)


def setup_signal_handler():
    signal.signal(signal.SIGINT, mathics3_basic_signal_handler)
