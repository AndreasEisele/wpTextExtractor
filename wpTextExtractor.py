#! /home/cl-home/eisele/lns-root-07/bin/python2.6 
# -*- coding: utf-8 -*-

__author__ = 'Andreas Eisele <eisele@dfki.de>'
__created__ = "Tue Jan 26 21:41:40 2010"
__id__ = '$Id: trymwlib.py 53 2010-01-27 13:53:08Z anei00 $'.strip("$")


# purpose of file:
# extract clear text from wikipedia articles


from time import clock, time
import sys
import os
import mwlib
import nltk
import wikipydia
import re
from optArgs import optParse, options, arguments
import mwlib
from mwlib.refine.compat import parse_txt
from mwlib.refine import core 
from mwlib.parser import nodes



# map all node types to the empty string
nodeTypes = [getattr(nodes,d) for d in dir(nodes)]
nodeTypes = [x for x in nodeTypes if type(x)==type]
node2markup = dict((n,'') for n in nodeTypes)
# except for those
node2markup[nodes.Section]='<s>'
node2markup[nodes.Item]='<i>'



def tree2string(tree):
    snippets = []
    _tree2string(tree,snippets)
    return ''.join(snippets)

def _tree2string(tree,snippets,level=0):
    snippets.append(node2markup[type(tree)])
    if options.trace: print '  '*level,type(tree)
    try:
        if type(tree)==nodes.ArticleLink:
            if not tree.children:
                if tree.text:
                    snippets.append(tree.text)
                else:
                    snippets.append(tree.target)
                if options.trace: 
                    print '  '*level,'ArticleLink: children:',len(tree.children)
                    print '  '*level,'target',tree.target.encode('utf-8')
                    print '  '*level,'text:',tree.text.encode('utf-8')
                return
        elif type(tree)==nodes.TagNode:
            return
        elif tree.text:
            if options.trace: print '  '*level,'text:',tree.text.encode('utf-8')
            snippets.append(tree.text)
    except AttributeError: pass
    try:
        for node in tree.children:
            _tree2string(node,snippets,level+1)
    except AttributeError: pass

def cleanup(text):
    # get rid of (nested) template calls 
    oldLen = 1E10
    while len(text)<oldLen:
        oldLen = len(text)
        text = re.sub('{[^{}]*}',' ',text)

    # little hack to change the order of 
    text = text.replace('."','".')
    
    #strip empty lines
    text = [x.strip() for x in text.split('\n')]
    text = [x for x in text if x and x not in '<i><s>']
    text = '\n'.join(text)

    return text


languages = [p.split(':') for p in '''en:english cz:czech da:danish nl:dutch et:estonian fi:finnish fr:french de:german el:greek it:italian no:norwegian pt:portuguese sl:slovene es:spanish sw:swedish tr:turkish'''.split()]

def lang2long(lang):
    for p in languages:
        if lang in p: return p[1]

def lang2short(lang):
    for p in languages:
        if lang in p: return p[0]

def raw2sentences(raw):
    tree = parse_txt(raw)
    text = tree2string(tree)
    lines = cleanup(text).split('\n')
    result = []
    for line in lines:
        if line.startswith('<'):
            result.append(line)
        else:
            result += sent_detector.tokenize(line.strip())
    return result


def main():
    global sent_detector
    optParse(
        trace__T=None,
        language__L='|'.join(l for p in languages for l in p),
        fromDump__D='',
        showType__S=None
        )

    sent_detector = nltk.data.load('tokenizers/punkt/%s.pickle' % lang2long(options.language))


    if options.fromDump:
        if options.fromDump.endswith('.gz'):
            source = os.popen('zcat %s' % options.fromDump)
        else:
            source = open(options.fromDump)
        currentLines = []
        for line in source:
            line = line.strip()
            if line.startswith('<title>'):
                print line
            elif line.startswith('<text'):
                currentLines.append(line.split('>',1)[1])
            elif currentLines:
                if line.endswith('</text>'):
                    currentLines.append(line.rsplit('<',1)[0])
                    print '\n'.join(raw2sentences('\n'.join(currentLines)))
                    currentLines = []
                else:
                    currentLines.append(line)
            

    else:
        for title in arguments:
            if title == 'Barack Obama' and options.language=='en':
                text = open('obama.src').read().decode('utf-8')
            else:
                text = wikipydia.query_text_raw(title, language=lang2short(options.language))['text']
            print '\n'.join(raw2sentences(text)).encode('utf-8')




if __name__ == "__main__":
    tc,tt=clock(),time()
    try: main()
    finally: print >> sys.stderr, "%.3f/%.3f seconds overall" % (clock()-tc, time()-tt)


