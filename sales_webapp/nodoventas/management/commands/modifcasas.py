from django.core.management.base import BaseCommand, CommandError
from ...models import Cliente, Duplex, Casa, Documento, Venta, FechaClave, Construccion, Expediente, Entrega

class Command(BaseCommand):
    help = 'Agrega objetos a todas las casas existentes.'

    #def add_arguments(self, parser):
        #parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        casas_todas = Casa.objects.all()
        for casa in casas_todas:
            if not(casa.venta.escritura) and not(casa.venta.recibo_apartado):
                reciboapartado = Documento.objects.create(tipo="Recibo de apartado")
                escritura = Documento.objects.create(tipo="Escritura completa")
                casa.venta.escritura = escritura
                casa.venta.recibo_apartado = reciboapartado
                casa.venta.save()
                self.stdout.write(self.style.SUCCESS(casa.casa_id + " modificada exitosamente."))
