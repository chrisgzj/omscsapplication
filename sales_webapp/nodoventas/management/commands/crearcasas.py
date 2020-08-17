from django.core.management.base import BaseCommand, CommandError
from ...models import Cliente, Duplex, Casa, Documento, Venta, FechaClave, Construccion, Expediente, Entrega

class Command(BaseCommand):
    help = 'Crea instancias vacias de n casas.'

    #def add_arguments(self, parser):
        #parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        calle = "Laureles"
        numeros = [13, 15, 17, 19]
        fachadas = ["BB", "BB", "BA", "BA"]
        num_duplexs = [67, 67, 66, 66]
        for i in range(len(numeros)):
            numero = numeros[i]
            fachada = fachadas[i]
            num_duplex = num_duplexs[i]
            casa_id = calle[0:3] + str(numero)
            casa = Casa.objects.filter(pk=casa_id)
            if casa:
                self.stdout.write(self.style.ERROR(casa_id + " ya existía."))
            else:
                duplex = Duplex.objects.filter(numero=num_duplex).first()
                if not duplex:
                    duplex = Duplex.objects.create(numero=num_duplex, fachada=fachada)
                apartado = Documento.objects.create(tipo="Comprobante de apartado")
                precalificacion = Documento.objects.create(tipo="Precalificacion")
                inscripcion = Documento.objects.create(tipo="Inscripcion")
                instruccion = Documento.objects.create(tipo="Instruccion")
                firma = FechaClave.objects.create()
                entrega = FechaClave.objects.create()
                recibo_apartado = Documento.objects.create(tipo="Recibo de apartado")
                escritura = Documento.objects.create(tipo="Escritura completa")
                venta = Venta.objects.create(apartado=apartado, precalificacion=precalificacion, inscripcion=inscripcion, instruccion=instruccion, firma=firma, entrega=entrega, recibo_apartado=recibo_apartado, escritura=escritura)
                fin_de_obra = FechaClave.objects.create()
                dtu = FechaClave.objects.create()
                construccion = Construccion.objects.create(fin_de_obra=fin_de_obra, dtu=dtu)
                fecha_exp = FechaClave.objects.create()
                nacimiento = Documento.objects.create(tipo="Acta de nacimiento")
                curp = Documento.objects.create(tipo="CURP")
                identificacion = Documento.objects.create(tipo="Identificacion oficial")
                rfc = Documento.objects.create(tipo="RFC")
                domicilio = Documento.objects.create(tipo="Comprobante de domicilio")
                conocimiento = Documento.objects.create(tipo="Conocimiento del inmueble")
                entidad = Documento.objects.create(tipo="Cartas entidad financiera")
                buro = Documento.objects.create(tipo="Cartas buro de credito")
                expunico = Documento.objects.create(tipo="Expediente Unico ISSSTE")
                talon = Documento.objects.create(tipo="Talon de pago")
                curso = Documento.objects.create(tipo="Curso cultura financiera")
                expediente = Expediente.objects.create(fecha=fecha_exp, nacimiento=nacimiento, curp=curp, identificacion=identificacion, rfc=rfc, domicilio=domicilio, conocimiento=conocimiento, entidad=entidad, buro=buro, expunico=expunico, talon=talon, curso=curso)
                reglamento = Documento.objects.create(tipo="Reglamento firmado")
                privacidad = Documento.objects.create(tipo="Aviso de privacidad")
                procedencia = Documento.objects.create(tipo="Procedenica ilicita")
                documentacion = Documento.objects.create(tipo="Recibo de documentacion")
                recepcion = Documento.objects.create(tipo="Convenio de recepcion")
                entrega = Entrega.objects.create(reglamento=reglamento, privacidad=privacidad, procedencia=procedencia, documentacion=documentacion, recepcion=recepcion)
                Casa.objects.create(casa_id=casa_id, calle=calle, numero=numero, duplex=duplex, venta=venta, construccion=construccion, expediente=expediente, entrega=entrega)
                self.stdout.write(self.style.SUCCESS(casa_id + " creada exitosamente."))
