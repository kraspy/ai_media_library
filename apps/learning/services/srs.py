from typing import Tuple


def calculate_next_review(
    quality: int, previous_interval: int, previous_ease: float, reps: int
) -> Tuple[int, float]:
    """
    Calculates the next review interval and ease factor using the SuperMemo-2 algorithm.

    Args:
        quality (int): The quality of the response (0-5).
                       5 - perfect response
                       4 - correct response after a hesitation
                       3 - correct response recalled with serious difficulty
                       2 - incorrect response; where the correct one seemed easy to recall
                       1 - incorrect response; the correct one remembered
                       0 - complete blackout.
        previous_interval (int): The previous interval in days.
        previous_ease (float): The previous easiness factor.
        reps (int): The number of successful repetitions so far.

    Returns:
        Tuple[int, float]: (next_interval, next_ease)
    """
    if quality < 3:
        # If the user failed, reset repetitions and interval
        return 1, previous_ease

    # Update ease factor
    # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    next_ease = previous_ease + (
        0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
    )
    if next_ease < 1.3:
        next_ease = 1.3

    # Calculate next interval
    if reps == 0:
        next_interval = 1
    elif reps == 1:
        next_interval = 6
    else:
        next_interval = int(previous_interval * previous_ease)

    return next_interval, next_ease
