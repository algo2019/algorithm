from BaseRole import BaseRole


class MinRole1(BaseRole):
    def __init__(self, offset=0):
        super(MinRole1, self).__init__()
        self.offset = offset

    def _self_check(self, h, m, s):
        if h == 9:
            if 1 <= m and s == self.offset:
                return True
        elif h == 10:
            if (m <= 14 or 31 <= m) and s == self.offset:
                return True
            if m == 14 and s == 50 + self.offset:
                return True
        elif h == 11:
            if m <= 29 and s == self.offset:
                return True
            if m == 29 and s == 50 + self.offset:
                return True
        elif h == 13:
            if 31 <= m and s == self.offset:
                return True
        elif h == 14:
            if s == self.offset:
                return True
            if m == 59 and s == 50 + self.offset:
                return True
        elif h == 21:
            if 1 <= m and s == self.offset:
                return True
        elif h == 22:
            if s == self.offset:
                return True
            if m == 59 and s == 50 + self.offset:
                return True
        elif h == 23:
            if 1 <= m <= 29 and s == self.offset:
                return True
            if 31 <= m and s == self.offset:
                return True
        elif h == 0:
            if s == self.offset:
                return True
            if m == 59 and s == 50 + self.offset:
                return True
        elif h == 1:
            if 1 <= m and s == self.offset:
                return True
        elif h == 2:
            if 1 <= m <= 29 and s == self.offset:
                return True
            if m == 29 and s == 50 + self.offset:
                return True
        return False


class MinRole5(BaseRole):
    def __init__(self, role1):
        super(MinRole5, self).__init__()
        self.__offset = role1.offset
        self.add_and_role(role1)

    def _self_check(self, h, m, s):
        if s == 50 + self.__offset or m % 5 == 0:
            return True
        return False


class MinRole10(BaseRole):
    def __init__(self, role1):
        super(MinRole10, self).__init__()
        self.add_and_role(role1)
        self.__offset = role1.offset

    def _self_check(self, h, m, s):
        if s == 50 + self.__offset or m % 10 == 0:
            return True
        return False


class MinRole15(BaseRole):
    def __init__(self, role1):
        super(MinRole15, self).__init__()
        self.add_and_role(role1)
        self.__offset = role1.offset

    def _self_check(self, h, m, s):
        if s == 50 + self.__offset or m % 15 == 0:
            return True
        return False


if __name__ == '__main__':
    role1 = MinRole1(2)
    role = role1
    for h in xrange(0, 24):
        for m in range(0, 60):
            for s in range(0, 60):
                if role.check(h, m, s):
                    print h, m, s
