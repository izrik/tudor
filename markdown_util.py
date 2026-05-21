import pycmarkgfm


def gfm_to_html(s):
    output = pycmarkgfm.gfm_to_html(s)
    output = output.replace('\\n', '<br/>')
    return output
