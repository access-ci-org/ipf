from setuptools_scm.version import ScmVersion, guess_next_version
import time
def mk_version( version ):
    refs = {
        'b': '{branch}',
        'd': '{dirty}',
        'dev': '{distance}',
        'n': '{node}',
        'nd': '{node_date}',
        't': '{time}',
        'T': int(time.time()),
        }
    parts = [
        # 'b',
        # 'd',
          'dev',
        # 'n',
        # 'nd',
        # 't',
          'T',
        ]
    # fmt_str = '{guessed}b{distance}'
    final = 'unknown'
    if version.exact :
        final = version.format_with( '{tag}' )
    else :
        fmt_str = '{guessed}.'
        fmt_str += '.'.join( [ f'{x}{refs[x]}' for x in parts ] )
        final = version.format_next_version( guess_next_version, fmt_str )
    return final
