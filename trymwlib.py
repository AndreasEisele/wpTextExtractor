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


#from pyparsing import nestedExpr



#from mwlib.uparser import simpleparse
#from mwlib.uparser import parseString, simpleparse
import mwlib
from mwlib.refine.compat import parse_txt
from mwlib.refine import core 
from mwlib.parser import nodes


def splitToSections(parse,lead=None,sections=None):
    if not sections: sections=[]
    # returns a list of subtrees of type section
    for child in parse.children:
        if type(child) == nodes.Section:
            sections.append(child)
        elif not sections:
            if not lead:
                lead = parse_txt(raw='== ==').children[0]
                lead.children=[]
            lead.children.append(child)
        else:
            splitToSections(child,lead,sections)
    return [lead]+sections


def extractText(simpleParse,collectedText=None):
    if collectedText==None: collectedText=[]
    for child in simpleParse.children:
        #print type(child),len(child.children)
        if type(child)==nodes.TagNode:
            pass
        elif len(child.children)==0:
            if child.text:
                collectedText.append(child.text)
                if options.trace: print child.text.encode('utf-8'),
            elif child.target:
                if type(child)==nodes.ArticleLink:
                    collectedText.append(child.target)
                    if options.trace: print child.target.encode('utf-8'),
            elif hasattr(child,'math') and child.math:
                collectedText.append(child.math)
                if options.trace: print child.math.encode('utf-8'),
            #elif type(child)==nodes.Node: pass
            else:
                print >> sys.stderr,'#######cannot handle',type(child),
                if options.trace:
                    print >> sys.stderr, dir(child)
                    for a in dir(child):
                        print >> sys.stderr, a, getattr(child,a)
        else:
            extractText(child,collectedText)
    return collectedText


def processArticle(text):
    tree = parse_txt(text)
    if options.trace:
        print '############# parse ###########'
        core.show(tree)
        print '############# sentences ###########'

    return processTree(tree)

def processTree(tree):
    return [processSection(section) for section in  splitToSections(tree)]
        
        


def processSection(section,splitAtNL=True):
    result = []
    extractedText = ''.join(extractText(section))


    '''
    expr = nestedExpr('{{','}}').leaveWhitespace()
    bracketedItems = expr.parseString('{{'+extractedText+'}}').asList()[0]
    res = []
    for item in bracketedItems:
        if not isinstance(item, list):
            res.append(item)
    extractedText = ' '.join(res)
    '''

    while len(set(extractedText) & set('{}'))==2:
        extractedText = re.sub('{[^{}]*}',' ',extractedText)

    # little hack to change the order of 
    extractedText = extractedText.replace('."','".')

    if splitAtNL: lines = extractedText.split('\n')
    else: lines = [extractedText]

    for text in lines:
        for sentence in sent_detector.tokenize(text.strip()):
            if sentence:
                result.append(sentence)
    return result



def processLines(lines):
    if not lines: return
    data='\n'.join(lines)
    data=data.split('>',1)[1]
    data=data.rsplit('<',1)[0]
    processArticle(data)


languages = [p.split(':') for p in '''en:english cz:czech da:danish nl:dutch et:estonian fi:finnish fr:french de:german el:greek it:italian no:norwegian pt:portuguese sl:slovene es:spanish sw:swedish tr:turkish'''.split()]

def lang2long(lang):
    for p in languages:
        if lang in p: return p[1]

def lang2short(lang):
    for p in languages:
        if lang in p: return p[0]


def main():
    global sent_detector
    optParse(
        trace__T=None,
        language__L='|'.join(l for p in languages for l in p)
        )

    sent_detector = nltk.data.load('tokenizers/punkt/%s.pickle' % lang2long(options.language))


    # print mwlib.__file__
    
    '''
    source = os.popen("zcat /share/emplus/corpora/wikipedia-201001/dewiki-20100117-pages-articles.xml.gz | gawk '/<title>/{print} /<text/,/<[/]text/'")

    lines = []
    for line in source:
        if line.strip().startswith('<title>'):
            processLines(lines)
            lines=[]
            print line

        else:
            lines.append(line)
            '''


    for title in arguments:
        if title == 'Barack Obama' and options.language=='en':
            text = open('obama.src').read().decode('utf-8')
        else:
            text = wikipydia.query_text_raw(title, language=lang2short(options.language))['text']

        if options.trace:
            print '############# ',title,', source ###########'
            print text.encode('utf-8')
        sections = processArticle(text)
        print '\n'.join(x for section in sections for x in section).encode('utf-8')






if __name__ == "__main__":
    tc,tt=clock(),time()
    try: main()
    finally: print >> sys.stderr, "%.3f/%.3f seconds overall" % (clock()-tc, time()-tt)


