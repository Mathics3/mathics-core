from mathics.core.evaluation import Evaluation
from mathics.repl import interactive_eval_loop

# dialog_nesting count controls the indentation
# for prompts In[] and Out[]. Each nesting
# adds two more spaces before the prompt text.
dialog_nesting_count: int = 0


def eval_Dialog(evaluation: Evaluation):
    """
    Evaluation method for Dialog[]
    """

    # Save prompt In/Out string state and line number.
    shell = evaluation.shell
    definitions = evaluation.definitions

    saved_line_number = definitions.get_line_no()
    saved_in_prefix = shell.in_prefix
    saved_out_prefix = shell.out_prefix

    # Change In/Out prompt strings to reflect new nesting.
    global dialog_nesting_count
    dialog_nesting_count += 1
    shell.in_prefix = ("  " * dialog_nesting_count) + shell.in_prefix
    shell.out_prefix = ("  " * dialog_nesting_count) + shell.out_prefix

    # Here is the nested interactive evaluation loop.
    result = interactive_eval_loop(
        shell,
        False,
        False,
        init_signal_handler=False,
        evaluation=evaluation,
    )

    # Restore prompt line number and In/Out prompt strings.
    dialog_nesting_count -= 1
    shell.in_prefix = saved_in_prefix
    shell.out_prefix = saved_out_prefix

    definitions.set_line_no(saved_line_number)

    # Reset evaluation variables that might might
    # cause abnormal evaluation termination.
    evaluation.timeout = False
    evaluation.stopped = False

    # Return last evaluation result if it exists.
    if hasattr(result, "last_eval"):
        return result.last_eval
    return None
