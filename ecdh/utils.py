# -*- coding: utf-8 -*-


def make_label(ncycle):
    ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
    return str(ordinal(ncycle)) + " cycle"


