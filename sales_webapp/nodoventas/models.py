from django.db import models
from random import random

class TipoCredito(models.Model):
    nombre = models.CharField(max_length=20, default="")
    def __str__(self):
        return f"{self.nombre}"

class GradoEstudios(models.Model):
    nombre = models.CharField(max_length=20, default="")
    def __str__(self):
        return f"{self.nombre}"

class Documento(models.Model):
    tipo = models.CharField(max_length = 50, default="")
    archivo = models.FileField(upload_to="docs/", null=True, blank=True)
    fecha = models.DateField(default="1900-01-01")
    def __str__(self):
        return f"{self.tipo}, {self.fecha}"

class FechaClave(models.Model):
    fecha = models.DateField(default="1900-01-01")
    aprox = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.fecha}, {self.aprox}"

class Vendedor(models.Model):
    nombre = models.CharField(max_length=64, default="")
    apellido = models.CharField(max_length=64, default="")
    equipo = models.CharField(max_length=10, default="")
    curp = models.CharField(max_length=20, default="")
    correo = models.EmailField(max_length=64, default="")
    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Expediente(models.Model):
    #Faltan varios los documentos propios de cada tipo de crédito.
    fecha = models.OneToOneField(FechaClave, null=True, on_delete=models.SET_NULL, related_name="expedientes_por_fecha")
    obs = models.TextField(default="")
    nacimiento = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="expedientes_por_nacimiento")
    curp = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="expedientes_por_curp")
    identificacion = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="expedientes_por_identificacion")
    rfc = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="expedientes_por_rfc")
    domicilio = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="expedientes_por_domicilio")
    #Info:
    conocimiento = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="expedientes_por_conocimiento")
    #Fovi:
    entidad = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="expedientes_por_entidad")
    buro = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="expedientes_por_buro")
    expunico = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="expedientes_por_expunico")
    talon = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="expedientes_por_talon")
    curso = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="expedientes_por_curso")

class Cliente(models.Model):
    nombre = models.CharField(max_length=64, default="")
    apellido = models.CharField(max_length=64, default="")
    fecha_nac = models.DateField(default="1900-01-01")
    curp = models.CharField(max_length=20, default="", blank=True)
    tipo_credito = models.ForeignKey(TipoCredito, null=True, on_delete=models.SET_NULL, related_name="clientes_por_credito")
    medio_contacto = models.CharField(max_length=64, default="", blank=True)
    vendedor = models.ForeignKey(Vendedor, null=True, on_delete=models.SET_NULL, related_name="clientes_por_vendedor")
    rfc = models.CharField(max_length=20, default="", blank=True)
    nss = models.CharField(max_length=20, default="", blank=True)
    correo = models.EmailField(max_length=64, default="", blank=True)
    tel_fijo = models.CharField(max_length=20, default="", blank=True)
    tel_celular = models.CharField(max_length=20, default="", blank=True)
    nombre_empresa = models.CharField(max_length=64, default="", blank=True)
    reg_patronal = models.CharField(max_length=20, default="", blank=True)
    grado_estudios = models.ForeignKey(GradoEstudios, null=True, on_delete=models.SET_NULL, related_name = "clientes_por_estudios", blank=True)
    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.tipo_credito})"

class ReferenciaPersonal(models.Model):
    cliente = models.ForeignKey(Cliente, null=True, on_delete=models.SET_NULL, related_name = "referencias_por_cliente")
    nombre_completo = models.CharField(max_length=128, default="", blank=True)
    parentesco = models.CharField(max_length=20, default="", blank=True)
    tel_fijo = models.CharField(max_length=20, default="", blank=True)
    tel_celular = models.CharField(max_length=20, default="", blank=True)
    def __str__(self):
        return f"{self.nombre_completo} - Referencia de {self.cliente}"

class Duplex(models.Model):
    numero = models.IntegerField(default=0)
    fachada = models.CharField(max_length=2, default="")
    def __str__(self):
        return f"{self.numero}D"

class Venta(models.Model):
    apartado = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="ventas_por_apartado")
    recibo_apartado = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="ventas_por_reciboapartado")
    precalificacion = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="ventas_por_precalificacion")
    obs_inicio = models.TextField(default="")
    inscripcion = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="ventas_por_inscripcion")
    instruccion = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="ventas_por_instruccion")
    escritura = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="ventas_por_escritura")
    firma = models.OneToOneField(FechaClave, null=True, on_delete=models.SET_NULL, related_name="ventas_por_firma")
    entrega = models.OneToOneField(FechaClave, null=True, on_delete=models.SET_NULL, related_name="ventas_por_entrega")
    obs_fin = models.TextField(default="")

class EtapaConstruccion(models.Model):
    nombre_etapa = models.TextField(default="", max_length=20)
    dias_etapa = models.IntegerField(default=0)
    def __str__(self):
        return self.nombre_etapa

class Construccion(models.Model):
    etapa_actual = models.ForeignKey(EtapaConstruccion, null=True, on_delete=models.SET_NULL, related_name="casas_por_etapa")
    inicio_etapa = models.DateField(default="1900-01-01")
    fin_de_obra = models.OneToOneField(FechaClave, null=True, on_delete=models.SET_NULL, related_name="construcciones_por_findeobra")
    dtu = models.OneToOneField(FechaClave, null=True, on_delete=models.SET_NULL, related_name="construcciones_por_dtu")
    solicitud_avaluo = models.OneToOneField(FechaClave, null=True, on_delete=models.SET_NULL, related_name="construcciones_por_solicitudavaluo")
    entrega_avaluo = models.OneToOneField(FechaClave, null=True, on_delete=models.SET_NULL, related_name="construcciones_por_entregaavaluo")
    monto_avaluo = models.IntegerField(default=0)
    doc_avaluo = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="construcciones_por_docavaluo")
    seg_calidad = models.OneToOneField(FechaClave, null=True, on_delete=models.SET_NULL, related_name="construcciones_por_segcalidad")
    migracion_cuv = models.OneToOneField(FechaClave, null=True, on_delete=models.SET_NULL, related_name="construcciones_por_migracioncuv")
    obs = models.TextField(default="", max_length=100)

class Entrega(models.Model):
    reglamento = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="entregas_por_reglamento")
    privacidad = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="entregas_por_privacidad")
    procedencia = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="entregas_por_procedencia")
    documentacion = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="entregas_por_documentacion")
    recepcion = models.OneToOneField(Documento, null=True, on_delete=models.SET_NULL, related_name="entregas_por_recepcion")

class Casa(models.Model):
    casa_id = models.CharField(max_length=5, primary_key=True)
    calle = models.CharField(max_length=20, default="")
    numero = models.IntegerField(default=0)
    duplex = models.ForeignKey(Duplex, null=True, on_delete=models.SET_NULL, related_name="casas_por_duplex")
    precio_venta = models.IntegerField(default=720000)
    cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.SET_NULL, related_name="casas_por_cliente")
    cliente_cony = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.SET_NULL, related_name="casas_por_clientecony")
    fecha_preap = models.DateTimeField(default="1900-01-01 00:00:00")
    vendedor = models.ForeignKey(Vendedor, null=True, blank=True, on_delete=models.SET_NULL, related_name="casas_por_vendedor")
    venta = models.OneToOneField(Venta, null=True, on_delete=models.SET_NULL, related_name="casas_por_venta")
    construccion = models.OneToOneField(Construccion, null=True, on_delete=models.SET_NULL, related_name="casas_por_construccion")
    expediente = models.OneToOneField(Expediente, null=True, on_delete=models.SET_NULL, related_name="casas_por_expediente")
    entrega = models.OneToOneField(Entrega, null=True, on_delete=models.SET_NULL, related_name="casas_por_entrega")
    def __str__(self):
        return f"{self.calle} {self.numero}"

class Saldo(models.Model):
    casa = models.ForeignKey(Casa, null=True, on_delete=models.SET_NULL, related_name="saldos_por_casa")
    nombre = models.CharField(max_length=20, default="")
    total_inicial = models.FloatField(default=0)
    def __str__(self):
        return f"{self.casa.casa_id} - {self.nombre}"

class ConceptoSaldo(models.Model):
    saldo = models.ForeignKey(Saldo, null=True, on_delete=models.SET_NULL, related_name="conceptos_por_saldo")
    nombre = models.CharField(max_length=20, default="")
    monto = models.FloatField(default=0)
    def __str__(self):
        return f"{self.saldo} - {self.nombre}"

class Accesorio(models.Model):
    casa = models.ForeignKey(Casa, null=True, on_delete=models.SET_NULL, related_name="accesorios_por_casa")
    tipo = models.IntegerField(default=0)
    estado = models.CharField(max_length=64, default="")
    limite = models.CharField(max_length=64, default="")
    def __str__(self):
        return f"{self.casa.casa_id} - {self.tipo}"

class TipoSeguimiento(models.Model):
    nombre = models.CharField(max_length=50, default="")
    def __str__(self):
        return f"{self.nombre}"

class Actualizacion(models.Model):
    cliente = models.ForeignKey(Cliente, null=True, on_delete=models.SET_NULL, related_name="actualizaciones_por_cliente")
    fecha = models.DateField(default="1900-01-01")
    tipo = models.ForeignKey(TipoSeguimiento, null=True, on_delete=models.SET_NULL, related_name="actualizaciones_por_tiposeguimiento")
    fecha_visita = models.DateField(null=True, blank=True)
    descripcion = models.TextField(default="", max_length=500)
    def __str__(self):
        return f"{self.cliente} - {self.tipo}"
