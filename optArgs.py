#! /usr/bin/env python2.3


__author__ = 'Andreas Eisele <eisele@dfki.de>'
__created__ = "Fri Feb  6 12:41:04 2004"
__date__ = ('$Date: 2004/02/09 08:23:13 $').strip("$")
__version__ = '$Revision: 1.2 $'.strip("$")


# purpose of file:

# a convenience wrapper around optparse


# todo:
# provide more informative help text
# support for boolean values



# completed

from optparse import OptionParser, Values


# provide names that can be imported
global options, arguments, optionsParsed
options=Values()
arguments=[]
optionsParsed=False

def key2opt(name):
    if len(name)==1: return "-"+name
    return "--"+name


def optParse(usage=None, version=None, **kw):
    global options, arguments, optionsParsed

    if optionsParsed:
        raise "optParse cannot be called twice"
    else:
        optionsParsed=True
    op=OptionParser(usage=usage, version=version)
    for key,val in kw.items():
        keys=[key2opt(k) for k in key.split("__")]
        if type(val) == type(1):
            otype="int"
        elif type(val) == type(1.0):
            otype="float"
        elif type(val)==type("") and "|" in val:
            choices=val.split("|")
            defVal=choices[0]
            op.add_option(default=defVal, choices=choices, help="one of: %s, [%s]"%(" ".join(choices),defVal), *keys)
            continue
        elif val==None:
            op.add_option(action="store_true", *keys)
            continue
        else:
            otype="string"
        op.add_option(default=val, type=otype, help="[%s]"%val,*keys)

    (opts, args)=op.parse_args()

    for a in args: arguments.append(a)
    options._update_loose(opts.__dict__)





def main():
    optParse(iOpt__i=1, sOpt__s="a")
    global options, arguments

    print "iOpt=",options.iOpt
    print "sOpt=",options.sOpt

    print "arguments=", arguments


if __name__ == "__main__":
    main()

