
class StartsEndsWith(object):

    """
    checks to see if 'foobar' starts or ends with any of the passed items:
        ['foo', 'bar', 'blah', 'duh']
        returns 'foo' in this case.
    raises
    """

    def __init__(self, prefixes=None, suffixes=None, case_insensitive=False):
        self.case_insensitive = case_insensitive

        self._prefix_term_dict = {}
        self._prefix_size_list = []

        self._suffix_term_dict = {}
        self._suffix_size_list = []

        if prefixes is None and suffixes is None:
            raise AttributeError('Some prefixes or suffixes must be defined')

        if prefixes is None:
            self._no_prefix = True
        else:
            self.add_prefixes(prefixes)
            self._no_prefix = False

        if suffixes is None:
            self._no_suffix = True
        else:
            self._no_suffix = False
            self.add_suffixes(suffixes)

    def add_suffixes(self, suffixes):
        self._make_term_dict(suffixes, self._suffix_term_dict, self._suffix_size_list)

    def add_prefixes(self, prefixes):
        self._make_term_dict(prefixes, self._prefix_term_dict, self._prefix_size_list)

    def _make_term_dict(self, terms, term_dict, size_list):
        term_dict.clear()
        size_list.clear()
        for term in terms:
            tmp_len = len(term)
            if tmp_len in term_dict:
                term_dict[tmp_len].append(term)
            else:
                term_dict[tmp_len] = [term]
        size_list.extend(term_dict)
        size_list.sort(reverse=True)

    def prefix(self, term):
        return self._check_term(term, prefix=True)

    def suffix(self, term):
        suffix, ret_term = self._check_term(term, prefix=False)
        return ret_term, suffix

    def check(self, term, allow_overlap=False, prefix_priority=True):

        if prefix_priority:
            prefix, ret_term = self._check_term(term, prefix=True)
            if allow_overlap:
                check_term = term
            else:
                check_term = ret_term
            suffix, ret_term = self._check_term(check_term, prefix=False)

        else:
            suffix, ret_term = self._check_term(term, prefix=False)
            if allow_overlap:
                check_term = term
            else:
                check_term = ret_term

            prefix, ret_term = self._check_term(check_term, prefix=True)

        if self._no_prefix:
            return ret_term, suffix
        elif self._no_suffix:
            return prefix, ret_term
        else:
            if allow_overlap:
                return prefix, suffix
            else:
                return prefix, ret_term, suffix

    def _check_term(self, term, prefix=True):
        if term is None:
            return None, None
        if prefix:
            term_dict = self._prefix_term_dict
            size_list = self._prefix_size_list
        else:
            term_dict = self._suffix_term_dict
            size_list = self._suffix_size_list

        term_len = len(term)

        if term_dict:
            for test_term_len in size_list:
                if term_len < test_term_len:
                    continue
                if prefix:
                    ret_ps_term = term[:test_term_len]
                    test_term = ret_ps_term.lower()
                else:
                    ret_ps_term = term[-test_term_len:]
                    test_term = ret_ps_term.lower()

                for psfix in term_dict[test_term_len]:
                    if psfix.lower() == test_term:
                        if prefix:
                            ret_term = term[test_term_len:]
                        else:
                            ret_term = term[:-test_term_len]
                        if ret_term == '':
                            ret_term = None
                        return ret_ps_term, ret_term
        return None, term

    def __call__(self, term, allow_overlap=False, prefix_priority=True):
        return self.check(term, allow_overlap=allow_overlap, prefix_priority=prefix_priority)
