"""
Classes to generate atomese without working with atomspace
"""
__author__ = "Anatoly Belikov"
__email__ = "abelikov@singularitynet.io"


class CAtom:
    def __hash__(self):
        return hash(str(self))


class CNode(CAtom):
    atom_type = None
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '({0} "{1}")'.format(self.atom_type, self.name.replace('"', '\\"')) 

    def recursive_print(self, result='', indent=''):
        return result + indent + str(self)



class CLink(CAtom):
    def __init__(self, *atoms):
        self.outgoing = atoms

    def __str__(self):
        outgoing = '\n'.join([str(x) for x in self.outgoing])
        return '({0} {1})'.format(self.atom_type, outgoing)

    def recursive_print(self, result='', indent=''):
        result += indent + '({0}'.format(self.atom_type)
        indent = indent + '    '
        for x in self.outgoing:
            result = x.recursive_print(result + '\n', indent)
        result += ')'
        return result


class CEvaluationLink(CLink):
    atom_type = 'EvaluationLink'

class CPredicateNode(CNode):
    atom_type = 'PredicateNode'

class CConceptNode(CNode):
    atom_type = 'ConceptNode'

class CMoleculeNode(CNode):
    atom_type = 'MoleculeNode'

class CMemberLink(CLink):
    atom_type = 'MemberLink'

class CListLink(CLink):
    atom_type = 'ListLink'

class CGeneNode(CNode):
    atom_type = 'GeneNode'

class CContextLink(CLink):
    atom_type = 'ContextLink'


class CSetLink(CLink):
    atom_type = 'SetLink'

    def __str__(self):
        # str is used for hash computation, so need to sort outgoing set for all unordered links
        outgoing = '\n'.join(sorted([str(x) for x in self.outgoing]))
        return '({0} {1})'.format(self.atom_type, outgoing)