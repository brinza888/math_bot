from functools import wraps

from models import User, LogRecord, get_db, get_user, close_db


def log_function_call(func):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        info = {
            'message': message.text,
            'args': args,
            'kwargs': kwargs,
        }
        try:
            result = func(message, *args, **kwargs)
        except Exception as ex:
            info['exception'] = str(ex)
            # raise ex  # TODO: environment variable to turn on/off
        else:
            info['result'] = result
            return result
        finally:
            db = get_db()
            user = get_user(db, message.from_user.id)
            if not user:
                user = User.new(
                    message.from_user.id,
                    message.from_user.last_name,
                    message.from_user.first_name,
                    message.from_user.username
                )
                db.add(user)
                db.commit()
            rec = LogRecord.new(user, func.__name__, message.chat.id, info)
            db.add(rec)
            db.commit()
            close_db()
    return wrapper
