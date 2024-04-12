#* header
import pcre2.exceptions
import pcre2

#* simple
e = [
    r'(',
    r'[A-Z]',
    r'|',
    r'[a-z]',
    r'|',
    r'[0-9]',
    r'|',
    r'[[:punct:]]',
    r'|',
    r' ',
    r'@',
    r')',
    r'{14,64}',
]
"".join([r'(',
         e[1],
         r'|', 
         e[3],
         r'|', 
         e[5],
         r'|', 
         e[7],
         r')', 
         ])

#* combinations
def or_(*s):
    return "".join(["(", r'|'.join(s), ")"])

def cond_(s):
    return or_(
        e[s[0]],
        e[s[1]],
        e[s[2]],
        e[s[3]],
        )

cond_([ 1, 3,  5,  7])

def require(*s):
    return "".join(["(?=", *s, ")"])

require(cond_([ 1,  3,  5,  7]))

def run(pats, string):
    patn = pcre2.compile(pats, jit=True)
    patn.jit_compile()
    ms = 'no match'
    try:
        match = patn.match(string)
        ms = match.substring()
    except pcre2.exceptions.MatchError:
        pass
    return ms

pats = require(cond_([ 1, 3,  5,  7]))
pats
run(pats, 'foo bar 091..##bar091..##bar091..##')

# incremental check
pats = require(
    cond_([ 1, 3,  5,  7]), 
    cond_([10, 3,  5,  7]), 
)
pats
run(pats, 'foo bar 091..##bar091..##bar091..##')

# full lookahead expression
pats = require(
    cond_([10, 3,  5,  7]), 
    cond_([ 1,10,  5,  7]), 
    cond_([ 1, 3, 10,  7]), 
    cond_([ 1, 3,  5, 10]), 
)
pats
run(pats, 'foo bar 091..##bar091..##bar091..##')

def and_(*s):
    return "".join(["(", r''.join(s), ")"])

def repeat_(min_, max_, *s):
    return "".join([*s, "{%d,%d}" % (min_, max_)])

pats = and_(
    or_(
        require(cond_([10, 3,  5,  7])),
        require(cond_([ 1,10,  5,  7])),
        require(cond_([ 1, 3, 10,  7])), 
        require(cond_([ 1, 3,  5, 10])), 
    ),
    repeat_(14, 64, cond_([1,  3,  5,  7]))
)

pats = and_(
    or_(
    require(cond_([10, 3,  5,  7])),
    require(cond_([ 1,10,  5,  7])),
    require(cond_([ 1, 3, 10,  7])), 
    require(cond_([ 1, 3,  5, 10])), 
)
    repeat_(14, 64, cond_([1,  3,  5,  7])),
)
# pats = '((?=(@|[a-z]|[0-9]|[[:punct:]]))(?=([A-Z]|@|[0-9]|[[:punct:]]))(?=([A-Z]|[a-z]|@|[[:punct:]]))(?=([A-Z]|[a-z]|[0-9]|@))([A-Z]|[a-z]|[0-9]|[[:punct:]]){14,64})'

pats = '^((?=[A-Z]))([A-Z]|[a-z]|[0-9]){14,64}$'
# simple sequential, no nesting
pats = '^((?=([A-Z]|@|[0-9])))([A-Z]|[a-z]|[0-9]){14,64}$'
# keep anchors $ and ^
pats = '^(?=([A-Z]|@|[0-9]|[[:punct:]]))([A-Z]|[a-z]|[0-9]|[[:punct:]]){14,64}$'
pats = '^(?=([a-z]|[0-9]|[[:punct:]]))(?=([A-Z]|[0-9]|[[:punct:]]))(?=([A-Z]|[a-z]|[[:punct:]]))(?=([A-Z]|[a-z]|[0-9]))([A-Z]|[a-z]|[0-9]|[[:punct:]]){14,64}$'
pats
[
    run(pats, 'foobar'), 
    run(pats, 'foobarfoobarfoobar'),
    run(pats, 'foo bar 091..##bar091..##bar091..##'),
    run(pats, 'FooBar10FooBar10FooBar10')
]
