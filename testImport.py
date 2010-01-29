
from time import clock, time
import sys
import os
import nltk
import wikipydia
from optArgs import optParse, options, arguments
from wpTextExtractor import wiki2sentences



languages = [p.split(':') for p in '''en:english cz:czech da:danish nl:dutch et:estonian fi:finnish fr:french de:german el:greek it:italian no:norwegian pt:portuguese sl:slovene es:spanish sw:swedish tr:turkish'''.split()]

def lang2long(lang):
    for p in languages:
        if lang in p: return p[1]

def lang2short(lang):
    for p in languages:
        if lang in p: return p[0]


def main():
    optParse(
        trace__T=None,
        language__L='|'.join(l for p in languages for l in p),
        fromDump__D='',
        showType__S=None,
        withTags__W=None
        )

    sent_detector = nltk.data.load('tokenizers/punkt/%s.pickle' % lang2long(options.language)).tokenize


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
                    print '\n'.join(wiki2sentences('\n'.join(currentLines),
                                                   sent_detector,False))
                    currentLines = []
                else:
                    currentLines.append(line)
            

    else:
        for title in arguments:
            if title == 'Barack Obama' and options.language=='en':
                text = open('obama.src').read().decode('utf-8')
            else:
                text = wikipydia.query_text_raw(title, language=lang2short(options.language))['text']
            if options.withTags:
                for s,t in zip(*wiki2sentences(text,sent_detector,True)):
                    print t[:4],s.encode('utf-8')
            else:
                print '\n'.join(wiki2sentences(text,sent_detector,False)).encode('utf-8')




if __name__ == "__main__":
    tc,tt=clock(),time()
    try: main()
    finally: print >> sys.stderr, "%.3f/%.3f seconds overall" % (clock()-tc, time()-tt)
