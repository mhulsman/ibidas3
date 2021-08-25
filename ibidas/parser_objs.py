import spark_parser
from spark_parser import GenericScanner, GenericParser, GenericToken, AST, GenericASTTraversal



class Token(GenericToken):#{{{
    def __repr__(self):
        if(self.attr is None):
            return str(self.kind)
        else:
            return str(self.kind) + ":" + str(self.attr)[:20]#}}}

class GenericASTRewriter(GenericASTTraversal):
    

    def preorder(self, node=None):
        if not isinstance(node, (AST,GenericToken)):
            return node
        name = 'n_' + self.typestring(node)
        if hasattr(self, name):
            func = getattr(self, name)
            node = func(node)
        else:
            node = self.default(node)

        if isinstance(node, AST):
            node.kids = [self.preorder(kid) for kid in node]

        name = name + '_exit'
        if hasattr(self, name):
            func = getattr(self, name)
            node = func(node)
        return node

    def postorder(self, node, context=None):
        if not isinstance(node, (AST,GenericToken)):
            return node
        name = 'x_' + self.typestring(node)
        if hasattr(self, name):
            func = getattr(self, name)
            node = func(node, context)
            return node

        if isinstance(node, AST):
            node[:] = [self.postorder(kid,context) for kid in node]

        name = 'n_' + self.typestring(node)
        if hasattr(self, name):
            func = getattr(self, name)
            if context is None:
                node = func(node)
            else:
                node = func(node, context)
        else:
            node = self.default(node)
        return node

    def default(self, node):
        return node#}}}

