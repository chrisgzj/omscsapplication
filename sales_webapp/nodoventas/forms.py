from django import forms
from .models import Venta, Casa, Documento, Construccion, FechaClave, Expediente, Cliente, ReferenciaPersonal, Actualizacion
from django.forms.widgets import FileInput, DateInput

class EdoExpForm(forms.ModelForm):
    class Meta:
        model = Expediente
        fields = ('obs',)

class GeneralesCasaForm(forms.ModelForm):
    class Meta:
        model = Casa
        fields = ('cliente','cliente_cony')

class VentaInicioForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ('obs_inicio',)

class VentaFinForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ('obs_fin',)

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ('fecha','archivo')
        widgets = {
            'archivo': FileInput()
        }

class ConstruccionForm(forms.ModelForm):
    class Meta:
        model = Construccion
        fields = ('etapa_actual','inicio_etapa','obs')

class FechaClaveForm(forms.ModelForm):
    class Meta:
        model = FechaClave
        fields = ('fecha','aprox')

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ('nombre','apellido','fecha_nac','curp','tipo_credito','medio_contacto','vendedor',\
        'rfc','nss','correo','tel_fijo','tel_celular','nombre_empresa','reg_patronal','grado_estudios')

class ReferenciaForm(forms.ModelForm):
    class Meta:
        model = ReferenciaPersonal
        fields = ('nombre_completo', 'parentesco', 'tel_fijo', 'tel_celular')

class ActualizacionClienteForm(forms.ModelForm):
    class Meta:
        model = Actualizacion
        fields = ('cliente', 'fecha', 'tipo', 'fecha_visita', 'descripcion')
