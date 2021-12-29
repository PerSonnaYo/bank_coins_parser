import zope.interface
from zope.interface import Interface, implementer
from zope.interface.interface import adapter_hooks
from zope.interface.adapter import AdapterRegistry

class IFile(zope.interface.Interface):
    body = zope.interface.Attribute(u'Структура парсера.')

class ISize(zope.interface.Interface):
    def getSize():
         'Return the size of an object.'
@implementer(IFile)
class File(object):
    body = 'foo bar'

@implementer(ISize)
class FileSize(object):
    __used_for__ = IFile
    def __init__(self, context):
        self.context = context
    def getSize(self):
        return len(self.context.body)

def hook(provided, object):
    adapter = registry.lookup1(zope.interface.providedBy(object),
                                provided, '')
    return adapter(object)

adapter_hooks.append(hook)
registry = AdapterRegistry()
registry.register([IFile], ISize, '', FileSize)
file = File()
size = ISize(file)
print(size.getSize())
adapter_hooks.remove(hook)

# class IFile(zope.interface.Interface):
#     body = zope.interface.Attribute(u'Структура парсера.')
#
# class ISize(zope.interface.Interface):
#     def getSize():
#          'Return the size of an object.'
# @implementer(IFile)
# class File(object):
#     body = 'foo bar'
#
# @implementer(ISize)
# class FileSize(object):
#     __used_for__ = IFile
#     def __init__(self, context):
#         self.context = context
#     def getSize(self):
#         return len(self.context.body)
#
# def hook(provided, object):
#     adapter = registry.lookup1(zope.interface.providedBy(object),
#                                 provided, '')
#     return adapter(object)
#
# adapter_hooks.append(hook)
# registry = AdapterRegistry()
# registry.register([IFile], ISize, '', FileSize)
# file = File()
# size = ISize(file)
# print(size.getSize())
# adapter_hooks.remove(hook)