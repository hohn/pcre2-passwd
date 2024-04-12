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

def anchor(*s):
    return "".join(["^(", r''.join(s), ")$"])

def require(*s):
    return "".join(["(?=.*", *s, ")"])

def and_(*s):
    return "".join(["(", r''.join(s), ")"])

def repeat_(min_, max_, *s):
    return "".join([*s, "{%d,%d}" % (min_, max_)])

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

def condition(s):
    return and_(
        require(e[s[0]]),
        require(e[s[1]]),
        require(e[s[2]]),
        )

def pat_from_choices(s):
    return or_(
        e[s[0]],
        e[s[1]],
        e[s[2]],
        e[s[3]],
    )
    
condition([ 3,  5,  7])

pats = anchor(
    and_(
        or_(
            condition([ 3, 5,  7]),
            condition([ 1, 5,  7]), 
            condition([ 1, 3,  7]), 
            condition([ 1, 3,  5]), 
        ),
        repeat_(14, 64, pat_from_choices([1,  3,  5,  7])),
    ))
pats
[
    run(pats, 'foobar'), 
    run(pats, 'foobarfoobarfoobar'),
    run(pats, 'foobarfoobarfoobar10'),
    run(pats, 'foo bar 091..##bar091..##bar091..##'),
    run(pats, 'FOObarfoobarfoobar##'),
    run(pats, 'FOOBARFOOBARFOOBAR10##'),
    run(pats, 'foobarfoobarfoobar10##'),
    run(pats, 'FooBar10FooBar10FooBar10')
]


# full lookahead expression
pats = require(
    condition([10, 3,  5,  7]), 
)
pats
run(pats, 'foo bar 091..##bar091..##bar091..##')


pats = and_(
    or_(
        require(condition([10, 3,  5,  7])),
        require(condition([ 1,10,  5,  7])),
        require(condition([ 1, 3, 10,  7])), 
        require(condition([ 1, 3,  5, 10])), 
    ),
    repeat_(14, 64, condition([1,  3,  5,  7]))
)

pats = and_(
    or_(
    require(condition([10, 3,  5,  7])),
    require(condition([ 1,10,  5,  7])),
    require(condition([ 1, 3, 10,  7])), 
    require(condition([ 1, 3,  5, 10])), 
)
    repeat_(14, 64, condition([1,  3,  5,  7])),
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
