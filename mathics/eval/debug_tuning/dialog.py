from mathics.core.evaluation import Evaluation
from mathics.repl import interactive_eval_loop

dialog_nesting_count: int = 0


def eval_Dialog(evaluation: Evaluation):

    # Save prompt In/Out string state and line number.
    shell = evaluation.shell

    saved_line_number = shell.get_last_line_number()
    saved_in_prefix = shell.in_prefix
    saved_out_prefix = shell.out_prefix

    # Change In/Out prompt strings to reflect new nesting.
    global dialog_nesting_count
    dialog_nesting_count += 1
    shell.in_prefix = ("  " * dialog_nesting_count) + shell.in_prefix
    shell.out_prefix = ("  " * dialog_nesting_count) + shell.out_prefix

    result = interactive_eval_loop(
        shell, False, False, init_signal_handler=False, evaluation=evaluation
    )

    # Restore prompt line number and In/Out prompt strings.
    shell.in_prefix = saved_in_prefix
    shell.lineno = saved_line_number
    shell.out_prefix = saved_out_prefix
    dialog_nesting_count -= 1

    # Return last evaluation result if it exists.
    if hasattr(result, "last_eval"):
        return result.last_eval
    return None
