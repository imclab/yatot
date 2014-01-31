#!/usr/bin/python
# -*- coding: utf-8 -*-

# ############################################################################
# cli.py
# Authors:
#   * -kc- <kevin.cousot at gmail.com>
#   * Rider Carrion <rider.carrion at gmail.com>
# Description: 
# This file is a modified version of python 2.7 cmd module which can be found
# here : http://hg.python.org/cpython/file/2.7/Lib/cmd.py
# ============================================================================
# Notes:
#
# ############################################################################

import yatot
import logging as log
import string

__all__ = ['CLI']

PROMPT = '> '
IDENTCHARS = string.ascii_letters + string.digits + '_' + '/'

class ACLI:


    prompt = PROMPT
    identchars = IDENTCHARS
    ruler = '='
    cmdprefix = '/'
    lastcmd = ''
    intro = None
    doc_leader = ""
    doc_header = "Documented commands (type /help <topic>):"
    misc_header = "Miscellaneous help topics:"
    undoc_header = "Undocumented commands:"
    nohelp = "*** No help on %s"
    use_rawinput = 1


    def __init__(self, completekey='tab', stdin=None, stdout=None):
        import sys
        if stdin is not None:
            self.stdin = stdin
        else:
            self.stdin = sys.stdin
        if stdout is not None:
            self.stdout = stdout
        else:
            self.stdout = sys.stdout
        self.cmdqueue = []
        self.completekey = completekey


    def cmdloop(self, intro=None):
        self.preloop()
        if self.use_rawinput and self.completekey:
            try:
                import readline
                self.old_completer = readline.get_completer()
                readline.set_completer(self.complete)
                readline.parse_and_bind(self.completekey+": complete")
            except ImportError:
                pass
        try:
            if intro is not None:
                self.intro = intro
            if self.intro:
                self.stdout.write(str(self.intro)+"\n")
            stop = None
            while not stop:
                if self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                else:
                    if self.use_rawinput:
                        try:
                            line = raw_input(self.prompt)
                        except EOFError:
                            line = 'EOF'
                    else:
                        self.stdout.write(self.prompt)
                        self.stdout.flush()
                        line = self.stdin.readline()
                        if not len(line):
                            line = 'EOF'
                        else:
                            line = line.rstrip('\r\n')
                    line = self.precmd(line)
                    stop = self.onecmd(line)
                    stop = self.postcmd(stop, line)

            self.postloop()
        finally:
            if self.use_rawinput and self.completekey:
                try:
                    import readline
                    readline.set_completer(self.old_completer)
                except ImportError:
                    pass


    def precmd(self, line):
        return line


    def postcmd(self, stop, line):
        return stop


    def preloop(self):
        pass


    def postloop(self):
        pass


    def parseline(self, line):
        line = line.strip()
        if not line:
            return None, None, line
        elif line[0] == '?':
            line = 'help ' + line[1:]
        elif line[0] == '!':
            if hasattr(self, 'do_shell'):
                line = 'shell ' + line[1:]
            else:
                return None, None, line
        elif line[0] == '/':
            i, n = 1, len(line)
            while i < n and line[i] in self.identchars: i = i+1
            cmd, arg = line[:i], line[i:].strip()
            return cmd, arg, line
        else:
            return None, None, line


    def onecmd(self, line):
        cmd, arg, line = self.parseline(line)
        if not line:
            return self.emptyline()
        if cmd is None:
            return self.default(line)
        self.lastcmd = line
        if line == 'EOF' :
            self.lastcmd = ''
        if cmd == '':
            return self.default(line)
        else:
            if line[0] == '/':
                cmd = cmd[1:]
                try:
                    func = getattr(self, 'do_' + cmd)
                except AttributeError:
                    return self.default(line)
                return func(arg)
            else:
                return self.default(line)


    def emptyline(self):
        pass


    def default(self, line):
        print ">>", line


    def completedefault(self, *ignored):
        return []


    def completenames(self, text, *ignored):
        dotext = 'do_'+text
        return [a[3:] for a in self.get_names() if a.startswith(dotext)]


    def complete(self, text, state):
        if state == 0:
            import readline
            origline = readline.get_line_buffer()
            line = origline.lstrip()
            stripped = len(origline) - len(line)
            begidx = readline.get_begidx() - stripped
            endidx = readline.get_endidx() - stripped
            if begidx>0:
                cmd, args, foo = self.parseline(line)
                if cmd == '':
                    compfunc = self.completedefault
                else:
                    try:
                        compfunc = getattr(self, 'complete_' + cmd)
                    except AttributeError:
                        compfunc = self.completedefault
            else:
                compfunc = self.completenames
            self.completion_matches = compfunc(text, line, begidx, endidx)
        try:
            return self.completion_matches[state]
        except IndexError:
            return None


    def get_names(self):
        # This method used to pull in base class attributes
        # at a time dir() didn't do it yet.
        return dir(self.__class__)


    def complete_help(self, *args):
        commands = set(self.completenames(*args))
        topics = set(a[5:] for a in self.get_names()
                     if a.startswith('help_' + args[0]))
        return list(commands | topics)


    def do_help(self, arg):
        if arg:
            # XXX check arg syntax
            try:
                func = getattr(self, 'help_' + arg)
            except AttributeError:
                try:
                    doc=getattr(self, 'do_' + arg).__doc__
                    if doc:
                        self.stdout.write("%s\n"%str(doc))
                        return
                except AttributeError:
                    pass
                self.stdout.write("%s\n"%str(self.nohelp % (arg,)))
                return
            func()
        else:
            names = self.get_names()
            cmds_doc = []
            cmds_undoc = []
            help = {}
            for name in names:
                if name[:5] == 'help_':
                    help[name[5:]]=1
            names.sort()
            # There can be duplicates if routines overridden
            prevname = ''
            for name in names:
                if name[:3] == 'do_':
                    if name == prevname:
                        continue
                    prevname = name
                    cmd=name[3:]
                    if cmd in help:
                        cmds_doc.append(cmd)
                        del help[cmd]
                    elif getattr(self, name).__doc__:
                        cmds_doc.append(cmd)
                    else:
                        cmds_undoc.append(cmd)
            self.stdout.write("%s\n"%str(self.doc_leader))
            self.print_topics(self.doc_header,   cmds_doc,   15,80)
            self.print_topics(self.misc_header,  help.keys(),15,80)
            self.print_topics(self.undoc_header, cmds_undoc, 15,80)


    def print_topics(self, header, cmds, cmdlen, maxcol):
        if cmds:
            self.stdout.write("%s\n"%str(header))
            if self.ruler:
                self.stdout.write("%s\n"%str(self.ruler * len(header)))
            self.columnize(cmds, maxcol-1)
            self.stdout.write("\n")


    def columnize(self, list, displaywidth=80):
        if not list:
            self.stdout.write("<empty>\n")
            return
        nonstrings = [i for i in range(len(list))
                        if not isinstance(list[i], str)]
        if nonstrings:
            raise TypeError, ("list[i] not a string for i in %s" %
                              ", ".join(map(str, nonstrings)))
        size = len(list)
        if size == 1:
            self.stdout.write('%s\n'%str(list[0]))
            return
        # Try every row count from 1 upwards
        for nrows in range(1, len(list)):
            ncols = (size+nrows-1) // nrows
            colwidths = []
            totwidth = -2
            for col in range(ncols):
                colwidth = 0
                for row in range(nrows):
                    i = row + nrows*col
                    if i >= size:
                        break
                    x = list[i]
                    colwidth = max(colwidth, len(x))
                colwidths.append(colwidth)
                totwidth += colwidth + 2
                if totwidth > displaywidth:
                    break
            if totwidth <= displaywidth:
                break
        else:
            nrows = len(list)
            ncols = 1
            colwidths = [0]
        for row in range(nrows):
            texts = []
            for col in range(ncols):
                i = row + nrows*col
                if i >= size:
                    x = ""
                else:
                    x = list[i]
                texts.append(x)
            while texts and not texts[-1]:
                del texts[-1]
            for col in range(len(texts)):
                texts[col] = texts[col].ljust(colwidths[col])
            self.stdout.write("%s\n"%str("  ".join(texts)))


banner = """
                       _______ _________ _______ _________
             |\     /|(  ___  )\__   __/(  ___  )\__   __/
             ( \   / )| (   ) |   ) (   | (   ) |   ) (
              \ (_) / | (___) |   | |   | |   | |   | |
               \   /  |  ___  |   | |   | |   | |   | |
                ) (   | (   ) |   | |   | |   | |   | |
                | |   | )   ( |   | |   | (___) |   | |
                \_/   |/     \|   )_(   (_______)   )_(
                                             
"""


welcomeMsg = """
Welcome to YATOT.

YATOT is a Tip Of the Tongue game.

Choose a word, and try to make me guess it, one hint at a time.
If I find it, please tell me so by typing /gg. At some point, I might
give up and ask you the answer.

Type /help to get the list of command, /exit to quit.

Good Luck & Have Fun !

"""

class CLI(ACLI):

    # CLASS CONSTRUCTOR
    def __init__(self, yatot):
        ACLI.__init__(self)
        self._yatot = yatot
        self.intro = banner +  welcomeMsg

    # DRAWS A PHRAPH
    def do_draw(self, args):
        path = self._yatot.drawGraph()
        print "Graph drawed: {0}".format(path)

    def help_draw(self):
        print "usage: /draw"
        print "-- Draw the graph."


    def do_dump(self, args):
        self._yatot.dumpGraph()


    def help_dump(self):
        print "usage: /dump"
        print "-- Dump the graph in graphml format."


    def do_exit(self, args):
        return -1


    def help_exit(self):
        print "usage: /exit"
        print "-- Exists YATOT."


    def do_gg(self, args):
        print "Great  I found your word !!!"
        print "\\o/ Great, I found your word \\o/"
        print "I needed {0} hints".format(len(self._yatot.getHints()))
        print self._yatot.getGraphInfos()
        print "Please play again !"
        return -1


    def help_gg(self):
        print "usage: /gg"
        print "-- Tells YATOT he found your word."


    def help_help(self):
        print "usage: /exit [command]"
        print "-- Get help."


    def do_infos(self, args):
        print "Hints given: {0}".format(len(self._yatot.getHints()))
        print self._yatot.getGraphInfos()


    def help_infos(self):
        print "usage: /infos"
        print "-- Prints infos about YATOT's current state."


    def do_welcome(self, args):
        print self.intro + "\n"


    def help_welcome(self):
        print "usage: /welcome"
        print "-- Print the welcome message"


    def default(self, hint):
        self._yatot._hintGiven(unicode(hint, "utf-8", "ignore"))


    def printMsg(self, msg):
        print msg

    
    def printRow(self, row):
        for key in row.keys():
            print "{0} : {1}".format(key, row[key])
