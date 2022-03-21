# -*- coding: utf-8 -*-

# Copyright (C) 2021-2022 Ilya Bezrukov, Stepan Chizhov, Artem Grishin
#
# This file is part of math_bot.
#
# math_bot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
#
# math_bot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from functools import wraps

from models import User, LogRecord, get_db, get_user, close_db
from config import Config


def log_function_call(log_unit_name: str):
    def decorator(func):
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
                if Config.DEBUG:
                    raise ex
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
                rec = LogRecord.new(user, log_unit_name, message.chat.id, info)
                db.add(rec)
                db.commit()
                close_db()
        return wrapper
    return decorator
