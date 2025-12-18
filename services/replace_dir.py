import shutil
from time import sleep

def replace_dir(src: str, dst: str, max_errors=10: int):
    """Rename a file or directory. If the destination already exists, attempt to
    delete it first. Pause and retry up to max_errors times before giving up in
    the event of an error."""

    errors = 0
    while True:
        try:
            # attempt to delete the destination directory
            shutil.rmtree(dst)
            continue
        except FileNotFoundError:
            # destination is gone so we're good to proceed
            break
        except Exception as e:
            # we got an unexpected error
            errors += 1
            if errors > max_errors:
                # if we've reached max_errors then give up
                raise e
            else:
                # wait and try again
                sleep(1)
    shutil.move(src, dst)

