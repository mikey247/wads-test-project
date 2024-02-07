#!/usr/bin/env python

import errno
import os

if __name__ == '__main__':
    if os.path.exists('./manage.py'):
        from util_wadsadmin import management
        management.main()
    else:
        raise FileNotFoundError(
            errno.ENOENT,
            "Please run this in the same top-level directory as manage.py",
        )
