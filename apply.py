#!/usr/bin/env python

import logging
_L = logging.getLogger(__name__)

import sys, os, shutil
from glob import glob
from subprocess import check_call, check_output

native=True

def getargs():
    import argparse
    P = argparse.ArgumentParser()
    P.add_argument('name',
                   default=os.path.basename(os.getcwd()),
                   help='Package name')
    P.add_argument('version', default='1', help='Package version')

    P.add_argument('-N','--myname',
                   default=os.environ.get('DEBFULLNAME') or os.environ.get('NAME') or os.environ.get('LOGNAME'),
                   help="Packager's name")
    P.add_argument('-E','--myemail',
                   default=os.environ.get('DEBEMAIL') or os.environ.get('EMAIL'),
                   help="Packager's email address")
    if not native:
        P.add_argument('--upname',
                    help="Name of upstream author/maintainer")
        P.add_argument('--upemail',
                    help="email address of upstream author/maintainer")
    P.add_argument("--template",
                   default=os.path.dirname(sys.argv[0]),
                   help="Directory containing template")
    P.add_argument("-d","--debug", action="store_true", default=False)

    args = P.parse_args()
    if native:
        args.upname = args.myname
        args.upemail = args.myemail
    return args

def getstr(prompt):
    sys.stdout.write(prompt+" > ")
    while True:
        V = sys.stdin.readline().strip()
        if V:
            return V

def prompt(args):
    if not args.myname:
        args.myname = getstr("Packager's (your) name")
        print "Hint: set 'export DEBFULLNAME=%s' to avoid this"%args.myname
    if not args.myemail:
        args.myemail = getstr("Packager's (your) email address")
        print "Hint: set 'export DEBEMAIL=%s' to avoid this"%args.myemail
    if not args.upname:
        args.upname = getstr("Upstream author/maintain name")
    if not args.upemail:
        args.upemail = getstr("Upstream author/maintain email address")

def main(args):
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    template = os.path.join(args.template, 'debian')
    if os.path.samefile(os.getcwd(), args.template):
        print >>sys.stderr, "Refuse to expand template onto itself"
        sys.exit(1)
    elif os.path.exists('debian'):
        print >>sys.stderr, "./debian already exists.  ignoring"
        sys.exit(0)
    elif not os.path.exists(template):
        print >>sys.stderr, "template missing", template
        sys.exit(0)

    A = {
        'name':args.name,
        'version':args.version,
        'myname':args.myname,
        'myemail':args.myemail,
        'upname':args.upname,
        'upemail':args.upemail,
    }
    print A

    try:
        _L.debug("copy %s as ./debian", template)
        check_call(["cp","-r",template,"."])
        files = check_output(['find','debian','-type','f']).splitlines()

        P = ['sed','-i',
                    '-e','s|libPACKAGENAME1|lib%(name)s%(version)s|g'%A,
                    '-e','s|PACKAGENAME|%(name)s|g'%A,
                    '-e','s|(1)|(%(version)s)|g'%A,
                    '-e','s|Your Name|%(myname)s|g'%A,
                    '-e','s|your.name@somewhere|%(myemail)s|g'%A,
            ]
        if native:
            P.extend([
                    '-e','s|Some One|%(myname)s|g'%A,
                    '-e','s|some.one@somewhere|%(myemail)s|g'%A,
            ])
        else:
            P.extend([
                    '-e','s|Some One|%(upname)s|g'%A,
                    '-e','s|some.one@somewhere|%(upemail)s|g'%A,
            ])
        P.extend(files)
        _L.debug("call: '%s'", ' '.join(P))
        check_call(P)
    except:
        if not args.debug:
            shutil.rmtree('debian', ignore_errors=True)
        raise

if __name__=='__main__':
    args = getargs()
    prompt(args)
    main(args)
