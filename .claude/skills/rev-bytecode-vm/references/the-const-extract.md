# Extracting constants — co_consts


co_consts holds every literal: strings, numbers, tuples, nested code
— flag-shaped strings and the expected values live here.

## The grep

    [c for c in code.co_consts if isinstance(c,str)]
