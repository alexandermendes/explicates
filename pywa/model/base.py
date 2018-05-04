# -*- coding: utf8 -*-

import datetime


class BaseDomainObject(object):

    def dictize(self):
        out = {}
        for col in self.__table__.c:
            obj = getattr(self, col.name)
            if isinstance(obj, datetime.datetime):
                obj = obj.isoformat()
            out[col.name] = obj
        return out
