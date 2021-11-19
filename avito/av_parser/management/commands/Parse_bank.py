from django.core.management.base import BaseCommand
import zope.interface
from zope.interface import implementer
from zope.interface.interface import adapter_hooks
from zope.interface.adapter import AdapterRegistry
from .parser_of_banks.parsing_procces import IParser
from .parser_of_banks.parsing_procces import Sberbank_pars
from .parser_of_banks.parsing_procces import Chelyabinvest_pars
from .parser_of_banks.parsing_procces import Chelind_pars
from .parser_of_banks.parsing_procces import Uralsib_pars

class Command(BaseCommand):
    help = 'Парсинг Банков'

    def handle(self, *args, **options):
        class ISize(zope.interface.Interface):
            def Start():
                'Begin a proccess of parsing'
            def Delete():
                'Delete the buffer table'
            def Clear():
                'Clear the table from selling elements'

        @implementer(ISize)
        class FileSize(object):
            __used_for__ = IParser

            def __init__(self, context):
                self.context = context

            def Start(self):
                self.context.start()

            def Delete(self):
                self.context.delete_sql_buffer()

            def Clear(self):
                self.context.clear_from_selling()

        def hook(provided, object):
            adapter = registry.lookup1(zope.interface.providedBy(object),
                                       provided, '')
            return adapter(object)

        adapter_hooks.append(hook)
        registry = AdapterRegistry()
        registry.register([IParser], ISize, '', FileSize)
        # x = bot.Command()

        file = Chelyabinvest_pars()
        file1 = Chelind_pars()
        file2 = Uralsib_pars()
        file3 = Sberbank_pars()
        # size = ISize(file)
        # size.Start()
        size1 = ISize(file1)
        size1.Start()
        # size2 = ISize(file2)
        # size2.Start()
        # size3 = ISize(file3)
        # size3.Start()
        # size1.Clear()
        # size1.Delete()
        adapter_hooks.remove(hook)