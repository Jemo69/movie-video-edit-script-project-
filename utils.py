from functools import wraps
from typing import TypedDict, Generic
import datetime
from typing import Any, Callable, Generic, Literal, TypedDict, TypeVar, Union
# Define type variables for generic use
T = TypeVar('T')
E = TypeVar('E', bound=Exception)

# --- Define the Success and Failure types using TypedDict ---
# 'data' will hold the successful result.
class Success(TypedDict, Generic[T]):
    data: T
    error: Literal[None] # Use Literal[None] to be explicit about no error

# 'error' will hold the exception on failure.
class Failure(TypedDict, Generic[E]):
    data: Literal[None] # Use Literal[None] to be explicit about no data
    error: E

# --- Define the overall Result type ---
# This Union represents either a Success or a Failure.
Result = Union[Success[T], Failure[E]]

# --- The TryCatch wrapper function ---
def try_catch(func: Callable[..., T], *args: Any, **kwargs: Any) -> Result[T, Exception]:
    """
    A generic function to wrap a callable and return a Result type.
    
    Args:
        func: The function to be executed.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.
    Returns:
        A Success object if the function executes without error,
        otherwise a Failure object containing the exception.
    """
    try:
        data = func(*args, **kwargs)
        return Success(data=data, error=None)
    except Exception as e:
        print(f"An error occurred: {e}")
        return Failure(data=None, error=e)
def time_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.datetime.now()
        duration = end_time - start_time
        print(f"Function '{func.__name__}' executed in {duration}")
        return result
    return wrapper
