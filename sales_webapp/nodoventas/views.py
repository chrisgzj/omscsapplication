from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from .models import Cliente, Duplex, Casa, Venta, Documento, Accesorio, Saldo, ConceptoSaldo, Actualizacion, FechaClave
from .forms import GeneralesCasaForm, VentaInicioForm, DocumentoForm, ConstruccionForm, FechaClaveForm, EdoExpForm, VentaFinForm, ClienteForm, ReferenciaForm, ActualizacionClienteForm
import json
import pytz
from datetime import datetime, date
from django.contrib.auth import logout

# Create your views here.
# Colores: info, warning, success, danger

def logout_view(request):
    logout(request)
    response = redirect('/accounts/login/')
    return response

def vencer_apartados():
    casas_todas = Casa.objects.all()
    for casa in casas_todas:
        desde_apartado = datetime.now(pytz.utc) - casa.fecha_preap
        en_horas = desde_apartado.days * 24 + desde_apartado.seconds / 3600
        if not(casa.cliente is None) and not(casa.venta.apartado.archivo):
            if en_horas > 50:
                casa.cliente = None
                casa.save()

def casa(request, casa_id):
    if request.method == "POST":
        casa = Casa.objects.get(pk=casa_id)
        tipo_credito = ""
        if casa.cliente:
            tipo_credito = casa.cliente.tipo_credito.nombre
        if request.POST['id_form'] == 'form_grales':
            form = GeneralesCasaForm(request.POST, instance=casa)
            if form.is_valid():
                form.save()
                casa.fecha_preap = datetime.now(pytz.utc)
                casa.save()
        if request.POST['id_form'] == 'form_inicioventa':
            form = VentaInicioForm(request.POST, instance = casa.venta)
            if form.is_valid():
                form.save()
            form = DocumentoForm(request.POST, request.FILES, instance = casa.venta.apartado, prefix="apart")
            if form.is_valid():
                form.save()
            form = DocumentoForm(request.POST, request.FILES, instance = casa.venta.recibo_apartado, prefix="reciboapart")
            if form.is_valid():
                form.save()
            form = DocumentoForm(request.POST, request.FILES, instance = casa.venta.precalificacion, prefix="precalif")
            if form.is_valid():
                form.save()
        if request.POST['id_form'] == 'form_construccion':
            form = ConstruccionForm(request.POST, instance = casa.construccion)
            if form.is_valid():
                form.save()
            form = FechaClaveForm(request.POST, instance = casa.construccion.fin_de_obra, prefix="fechafin")
            if form.is_valid():
                form.save()
            form = FechaClaveForm(request.POST, instance = casa.construccion.dtu, prefix="fechadtu")
            if form.is_valid():
                form.save()
        if request.POST['id_form'] == 'form_edoexpediente':
            form = EdoExpForm(request.POST, instance = casa.expediente)
            if form.is_valid():
                form.save()
            form = FechaClaveForm(request.POST, instance = casa.expediente.fecha, prefix="fechaexp")
            if form.is_valid():
                form.save()
        if request.POST['id_form'] == 'form_cierreventa':
            form = DocumentoForm(request.POST, request.FILES, instance = casa.venta.inscripcion, prefix="inscrip")
            if form.is_valid():
                form.save()
            form = DocumentoForm(request.POST, request.FILES, instance = casa.venta.instruccion, prefix="instrucc")
            if form.is_valid():
                form.save()
            form = DocumentoForm(request.POST, request.FILES, instance = casa.venta.escritura, prefix="escritura")
            if form.is_valid():
                form.save()
            form = FechaClaveForm(request.POST, instance = casa.venta.firma, prefix="fechafirma")
            if form.is_valid():
                form.save()
            form = FechaClaveForm(request.POST, instance = casa.venta.entrega, prefix="fechaentrega")
            if form.is_valid():
                form.save()
            form = VentaFinForm(request.POST, instance = casa.venta)
            if form.is_valid():
                form.save()
        if request.POST['id_form'] == 'form_expediente':
            form = DocumentoForm(request.POST, request.FILES, instance = casa.expediente.nacimiento, prefix="nacimiento")
            if form.is_valid():
                form.save()
            form = DocumentoForm(request.POST, request.FILES, instance = casa.expediente.curp, prefix="curp")
            if form.is_valid():
                form.save()
            form = DocumentoForm(request.POST, request.FILES, instance = casa.expediente.identificacion, prefix="identificacion")
            if form.is_valid():
                form.save()
            form = DocumentoForm(request.POST, request.FILES, instance = casa.expediente.rfc, prefix="rfc")
            if form.is_valid():
                form.save()
            form = DocumentoForm(request.POST, request.FILES, instance = casa.expediente.domicilio, prefix="domicilio")
            if form.is_valid():
                form.save()
            if tipo_credito == "INFONAVIT" or tipo_credito == "INFONAVIT CONYUGAL" or tipo_credito == "COFINAVIT":
                form = DocumentoForm(request.POST, request.FILES, instance = casa.expediente.conocimiento, prefix="conocimiento")
                if form.is_valid():
                    form.save()
            if tipo_credito == "FOVISSSTE" or tipo_credito == "FOVISSSTE CONYUGAL":
                form = DocumentoForm(request.POST, request.FILES, instance = casa.expediente.entidad, prefix="entidad")
                if form.is_valid():
                    form.save()
                form = DocumentoForm(request.POST, request.FILES, instance = casa.expediente.buro, prefix="buro")
                if form.is_valid():
                    form.save()
                form = DocumentoForm(request.POST, request.FILES, instance = casa.expediente.expunico, prefix="expunico")
                if form.is_valid():
                    form.save()
                form = DocumentoForm(request.POST, request.FILES, instance = casa.expediente.talon, prefix="talon")
                if form.is_valid():
                    form.save()
                form = DocumentoForm(request.POST, request.FILES, instance = casa.expediente.curso, prefix="curso")
                if form.is_valid():
                    form.save()
        if request.POST['id_form'] == 'form_accesorios':
            nuevos = []
            if len(request.POST['list_acces']) > 0:
                nuevos = [int(float(x)) for x in request.POST['list_acces'][:-1].split("/")]
            originales = casa.accesorios_por_casa.all()
            for orig in originales:
                if orig.tipo in nuevos:
                    nuevos.remove(orig.tipo)
                else:
                    orig.delete()
            for nvo in nuevos:
                if nvo > 0:
                    Accesorio.objects.create(casa=casa, tipo=nvo)
        if request.POST['id_form'] == 'form_saldos':
            for sld_elim in casa.saldos_por_casa.all():
                sld_elim.conceptos_por_saldo.all().delete()
            casa.saldos_por_casa.all().delete()
            obj_saldos = json.loads(request.POST['list_saldos'])
            for sld in obj_saldos:
                saldo_tmp = Saldo.objects.create(casa=casa, nombre=sld['concepto'], total_inicial=sld['monto'])
                if 'subsaldos' in sld:
                    for sub_sl in sld['subsaldos']:
                        subsl_tmp = ConceptoSaldo.objects.create(saldo=saldo_tmp, nombre=sub_sl['concepto'], monto=sub_sl['monto'])
        if request.POST['id_form'] == 'form_entrega':
            form = DocumentoForm(request.POST, request.FILES, instance = casa.entrega.reglamento, prefix="reglamento")
            if form.is_valid():
                form.save()
            form = DocumentoForm(request.POST, request.FILES, instance = casa.entrega.privacidad, prefix="privacidad")
            if form.is_valid():
                form.save()
            form = DocumentoForm(request.POST, request.FILES, instance = casa.entrega.procedencia, prefix="procedencia")
            if form.is_valid():
                form.save()
            form = DocumentoForm(request.POST, request.FILES, instance = casa.entrega.documentacion, prefix="documentacion")
            if form.is_valid():
                form.save()
            form = DocumentoForm(request.POST, request.FILES, instance = casa.entrega.recepcion, prefix="recepcion")
            if form.is_valid():
                form.save()
    usuario = request.user.username
    if usuario == "" or usuario is None:
        response = redirect('/accounts/login/')
        return response
    grupo = request.user.groups.first()
    if grupo.name == "Ventas":
        return redirect('/listaclientes/')
    vencer_apartados()
    edita_generales = False
    edita_venta = False
    edita_expediente = False
    edita_construccion = False
    edita_saldos = False
    edita_accesorios = False
    edita_entrega = False
    if grupo.name == "Admin" or grupo.name == "Coord":
        edita_generales = True
        edita_venta = True
        edita_expediente = True
        edita_saldos = True
        edita_accesorios = True
        edita_entrega = True
    if grupo.name == "Admin":
        edita_construccion = True
    casa = Casa.objects.get(pk=casa_id)
    if casa.cliente:
        tipo_credito = casa.cliente.tipo_credito.nombre
    else:
        tipo_credito = ""
    form_gralcasa = GeneralesCasaForm(instance=casa)
    form_ini_venta = VentaInicioForm(instance=casa.venta)
    form_apartado = DocumentoForm(instance=casa.venta.apartado, prefix="apart")
    form_reciboapartado = DocumentoForm(instance=casa.venta.recibo_apartado, prefix="reciboapart")
    form_precalif = DocumentoForm(instance=casa.venta.precalificacion, prefix="precalif")
    form_construccion = ConstruccionForm(instance=casa.construccion)
    form_fechafin = FechaClaveForm(instance=casa.construccion.fin_de_obra, prefix="fechafin")
    form_fechadtu = FechaClaveForm(instance=casa.construccion.dtu, prefix="fechadtu")
    form_edoexp = EdoExpForm(instance=casa.expediente)
    form_fechaexp = FechaClaveForm(instance=casa.expediente.fecha, prefix="fechaexp")
    form_fin_venta = VentaFinForm(instance=casa.venta)
    form_inscripcion = DocumentoForm(instance=casa.venta.inscripcion, prefix="inscrip")
    form_instruccion = DocumentoForm(instance=casa.venta.instruccion, prefix="instrucc")
    form_escritura = DocumentoForm(instance=casa.venta.escritura, prefix="escritura")
    form_fechafirma = FechaClaveForm(instance=casa.venta.firma, prefix="fechafirma")
    form_fechaentrega = FechaClaveForm(instance=casa.venta.entrega, prefix="fechaentrega")
    form_nacimiento = DocumentoForm(instance=casa.expediente.nacimiento, prefix="nacimiento")
    form_curp = DocumentoForm(instance=casa.expediente.curp, prefix="curp")
    form_identificacion = DocumentoForm(instance=casa.expediente.identificacion, prefix="identificacion")
    form_rfc = DocumentoForm(instance=casa.expediente.rfc, prefix="rfc")
    form_domicilio = DocumentoForm(instance=casa.expediente.domicilio, prefix="domicilio")
    form_reglamento = DocumentoForm(instance=casa.entrega.reglamento, prefix="reglamento")
    form_privacidad = DocumentoForm(instance=casa.entrega.privacidad, prefix="privacidad")
    form_procedencia = DocumentoForm(instance=casa.entrega.procedencia, prefix="procedencia")
    form_documentacion = DocumentoForm(instance=casa.entrega.documentacion, prefix="documentacion")
    form_recepcion = DocumentoForm(instance=casa.entrega.recepcion, prefix="recepcion")
    if tipo_credito == "INFONAVIT" or tipo_credito == "INFONAVIT CONYUGAL" or tipo_credito == "COFINAVIT":
        form_conocimiento = DocumentoForm(instance=casa.expediente.conocimiento, prefix="conocimiento")
        tiene_info = True
    else:
        form_conocimiento = None
        tiene_info = False
    if tipo_credito == "FOVISSSTE" or tipo_credito == "FOVISSSTE CONYUGAL":
        form_entidad = DocumentoForm(instance=casa.expediente.entidad, prefix="entidad")
        form_buro = DocumentoForm(instance=casa.expediente.buro, prefix="buro")
        form_expunico = DocumentoForm(instance=casa.expediente.expunico, prefix="expunico")
        form_talon = DocumentoForm(instance=casa.expediente.talon, prefix="talon")
        form_curso = DocumentoForm(instance=casa.expediente.curso, prefix="curso")
        tiene_fovi = True
    else:
        form_entidad = None
        form_buro = None
        form_expunico = None
        form_talon = None
        form_curso = None
        tiene_fovi = False
    es_conyugal = "CONY" in tipo_credito
    if not(casa.venta.firma.aprox):
        color_apartado = "info"
    else:
        if casa.fecha_preap.year == 1900:
            color_apartado = ""
        else:
            if casa.venta.apartado.archivo:
                desde_apartado = datetime.now(pytz.utc) - casa.fecha_preap
                if desde_apartado.days > 20:
                    if desde_apartado.days < 30:
                        color_apartado = "warning"
                    else:
                        color_apartado = "danger"
                else:
                    color_apartado = "success"
            else:
                color_apartado = "danger"
    if casa.construccion.etapa_actual:
        if casa.construccion.fin_de_obra.aprox:
            desde_etapa = date.today() - casa.construccion.inicio_etapa
            if desde_etapa.days > casa.construccion.etapa_actual.dias_etapa:
                if desde_etapa.days > casa.construccion.etapa_actual.dias_etapa + 2:
                    color_construccion = "danger"
                else:
                    color_construccion = "warning"
            else:
                color_construccion = "success"
        else:
            color_construccion = "info"
    else:
        color_construccion = ""
    if not(casa.venta.firma.aprox):
        color_expediente = "info"
    else:
        if casa.fecha_preap.year == 1900:
            color_expediente = ""
        else:
            if casa.expediente.fecha.aprox:
                if casa.construccion.fin_de_obra.aprox:
                    color_expediente = "warning"
                else:
                    color_expediente = "danger"
            else:
                color_expediente = "success"
    if not(casa.venta.firma.aprox):
        color_firma = "info"
    else:
        if casa.fecha_preap.year == 1900 or casa.construccion.fin_de_obra.aprox:
            color_firma = ""
        else:
            ult_fecha = max(casa.fecha_preap.date(), casa.construccion.fin_de_obra.fecha)
            desde_ultfecha = date.today() - ult_fecha
            if desde_ultfecha.days < 10:
                color_firma = "success"
            else:
                if desde_ultfecha.days > 20:
                    color_firma = "danger"
                else:
                    color_firma = "warning"



    precio_raw = casa.precio_venta
    precio_venta = '{:,.2f}'.format(precio_raw)
    subsaldos = [sld.conceptos_por_saldo.all() for sld in casa.saldos_por_casa.all()]

    context = {
        "nombre_casa" : casa,
        "color_apartado": color_apartado,
        "color_construccion": color_construccion,
        "color_expediente": color_expediente,
        "color_pago": "",
        "color_firma": color_firma,
        "color_entrega": "",
        "nombre_cliente": casa.cliente,
        "vendedor": casa.vendedor,
        "duplex": casa.duplex,
        "fachada": casa.duplex.fachada,
        "edita_generales": edita_generales,
        "edita_venta": edita_venta,
        "edita_expediente": edita_expediente,
        "edita_construccion": edita_construccion,
        "edita_saldos": edita_saldos,
        "edita_accesorios": edita_accesorios,
        "edita_entrega": edita_entrega,
        "form_ini_venta": form_ini_venta,
        "form_gralcasa": form_gralcasa,
        "form_apartado": form_apartado,
        "form_reciboapartado": form_reciboapartado,
        "form_precalif": form_precalif,
        "form_construccion": form_construccion,
        "form_fechafin": form_fechafin,
        "form_fechadtu": form_fechadtu,
        "form_edoexp": form_edoexp,
        "form_fechaexp": form_fechaexp,
        "form_fin_venta": form_fin_venta,
        "form_inscripcion": form_inscripcion,
        "form_instruccion": form_instruccion,
        "form_escritura": form_escritura,
        "form_fechafirma": form_fechafirma,
        "form_fechaentrega": form_fechaentrega,
        "form_nacimiento": form_nacimiento,
        "form_identificacion": form_identificacion,
        "form_curp": form_curp,
        "form_rfc": form_rfc,
        "form_domicilio": form_domicilio,
        "precio_venta": precio_venta,
        "accesorios": casa.accesorios_por_casa.all(),
        "saldos": casa.saldos_por_casa.all(),
        "subsaldos": subsaldos,
        "form_reglamento": form_reglamento,
        "form_privacidad": form_privacidad,
        "form_procedencia": form_procedencia,
        "form_documentacion": form_documentacion,
        "form_recepcion": form_recepcion,
        "tipo_credito": tipo_credito,
        "form_conocimiento": form_conocimiento,
        "tiene_info": tiene_info,
        "form_entidad": form_entidad,
        "form_buro": form_buro,
        "form_expunico": form_expunico,
        "form_talon": form_talon,
        "form_curso": form_curso,
        "tiene_fovi": tiene_fovi,
        "es_conyugal": es_conyugal,
        "usuario": usuario
    }
    return render(request,"1110/index.html", context)

def cliente(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            curp_nvo = form.cleaned_data['curp'].strip()
            nss_nvo = form.cleaned_data['nss'].strip()
            nombre_nvo = form.cleaned_data['nombre'].strip()
            apellido_nvo = form.cleaned_data['apellido'].strip()
            cliente_repetido = 0
            if (curp_nvo != '' and Cliente.objects.filter(curp=curp_nvo)):
                 cliente_repetido = Cliente.objects.get(curp=curp_nvo).id
            if (nss_nvo != '' and Cliente.objects.filter(nss=nss_nvo)):
                cliente_repetido = Cliente.objects.get(nss=nss_nvo).id
            if Cliente.objects.filter(nombre=nombre_nvo, apellido=apellido_nvo):
                cliente_repetido = Cliente.objects.filter(nombre=nombre_nvo, apellido=apellido_nvo).first().id
            if cliente_repetido != 0:
                return redirect('/errorcliente_' + str(cliente_repetido) + '/')
            else:
                form.cleaned_data['nombre'] = form.cleaned_data['nombre'].strip()
                form.cleaned_data['apellido'] = form.cleaned_data['apellido'].strip()
                cliente = form.save()
                form = ReferenciaForm(request.POST, prefix="ref1")
                if form.is_valid():
                    ref = form.save()
                    ref.cliente = cliente
                    ref.save()
                form = ReferenciaForm(request.POST, prefix="ref2")
                if form.is_valid():
                    ref = form.save()
                    ref.cliente = cliente
                    ref.save()
    usuario = request.user.username
    if usuario == "" or usuario is None:
        response = redirect('/accounts/login/')
    vencer_apartados()
    cliente_form = ClienteForm()
    ref1_form = ReferenciaForm(prefix="ref1")
    ref2_form = ReferenciaForm(prefix="ref2")
    context = {
        "cliente_form": cliente_form,
        "ref1_form": ref1_form,
        "ref2_form": ref2_form,
        "mostrar_botones": False,
        "usuario": usuario
    }
    return render(request,'altacliente/index.html',context)

def modifcliente(request, cliente_id):
    if request.method == "POST":
        if request.POST['id_form'] == 'form_datoscliente':
            cliente = Cliente.objects.get(pk=cliente_id)
            form = ClienteForm(request.POST, instance=cliente)
            if form.is_valid():
                curp_nvo = form.cleaned_data['curp'].strip()
                nss_nvo = form.cleaned_data['nss'].strip()
                nombre_nvo = form.cleaned_data['nombre'].strip()
                apellido_nvo = form.cleaned_data['apellido'].strip()
                cliente_repetido = 0
                if (curp_nvo != '' and Cliente.objects.filter(curp=curp_nvo)):
                     cliente_repetido = Cliente.objects.get(curp=curp_nvo).id
                if (nss_nvo != '' and Cliente.objects.filter(nss=nss_nvo)):
                    cliente_repetido = Cliente.objects.get(curp=curp_nvo).id
                if Cliente.objects.filter(nombre=nombre_nvo, apellido=apellido_nvo):
                    cliente_repetido = Cliente.objects.get(curp=curp_nvo).id
                if cliente_repetido != 0 and str(cliente_repetido) != str(cliente_id):
                    return redirect('/errorcliente_' + str(cliente_repetido) + '/')
                else:
                    form.cleaned_data['nombre'] = form.cleaned_data['nombre'].strip()
                    form.cleaned_data['apellido'] = form.cleaned_data['apellido'].strip()
                    form.save()
                form = ReferenciaForm(request.POST, prefix="ref1", instance=cliente.referencias_por_cliente.all().first())
                if form.is_valid():
                    form.save()
                form = ReferenciaForm(request.POST, prefix="ref2", instance=cliente.referencias_por_cliente.all().last())
                if form.is_valid():
                    ref = form.save()
        if request.POST['id_form'] == 'form_botonactualizacion':
            id_cliente = request.POST['idcliente']
            request.session['idcliente'] = id_cliente
            return redirect('/seguimientocliente/')
        if request.POST['id_form'] == 'form_botonactualizacionlista':
            id_cliente = request.POST['idcliente']
            request.session['idcliente'] = id_cliente
            return redirect('/listaseguimientocliente/')
    usuario = request.user.username
    if usuario == "" or usuario is None:
        response = redirect('/accounts/login/')
        return response
    email_usuario = request.user.email
    grupo = request.user.groups.first()
    cliente = Cliente.objects.get(pk=cliente_id)
    email_decliente = cliente.vendedor.correo
    if grupo.name == "Ventas" and email_usuario != email_decliente:
        return redirect ('/listaclientes/')
    cliente_form = ClienteForm(instance=cliente)
    ref1_form = ReferenciaForm(instance=cliente.referencias_por_cliente.all().first(), prefix="ref1")
    ref2_form = ReferenciaForm(instance=cliente.referencias_por_cliente.all().last(), prefix="ref2")
    casa = cliente.casas_por_cliente.first()
    context = {
        "cliente_form": cliente_form,
        "ref1_form": ref1_form,
        "ref2_form": ref2_form,
        "mostrar_botones": True,
        "cliente": cliente,
        "casa": casa,
        "usuario": usuario
    }
    return render(request,'altacliente/index.html',context)

def listaclientes(request):
    usuario = request.user.username
    if usuario == "" or usuario is None:
        response = redirect('/accounts/login/')
        return response
    vencer_apartados()
    context = {
        "clientes": Cliente.objects.all(),
        "correo_usuario": request.user.email,
        "ver_todos": request.user.groups.first().name != "Ventas",
        "usuario": usuario
    }
    return render(request,'listaclientes/index.html', context)

def listacasas(request, casas, nom_titulo):
    usuario = request.user.username
    if usuario == "" or usuario is None:
        response = redirect('/accounts/login/')
        return response
    grupo = request.user.groups.first()
    if grupo.name == "Ventas":
        return redirect('/listaclientes/')
    vencer_apartados()
    context = {
        "casas": casas,
        "nom_titulo": nom_titulo,
        "usuario": usuario
    }
    return render(request,'listacasas/index.html', context)

def devolver_nombre(casa):
    if casa.cliente:
        return casa.cliente.nombre
    return "ZZZ"

def lista_porestado(request, nom_estado):
    casas = None
    if nom_estado == "Todas":
        casas = Casa.objects.all()
    if nom_estado == "Disponibles":
        casas = Casa.objects.filter(cliente=None)
    if nom_estado == "Escrituradas":
        fechas_exactas = FechaClave.objects.filter(aprox=False)
        ventas_cerradas = Venta.objects.filter(firma__in=fechas_exactas)
        casas = Casa.objects.filter(venta__in=ventas_cerradas)
    if nom_estado == "Pendientes":
        nom_estado = "En proceso"
        fechas_aprox = FechaClave.objects.filter(aprox=True)
        ventas_abiertas = Venta.objects.filter(firma__in=fechas_aprox)
        casas = Casa.objects.filter(venta__in=ventas_abiertas).exclude(cliente=None)
    casas = sorted(casas, key=devolver_nombre)
    return listacasas(request, casas, nom_estado)


def lista_porcalle(request, nom_calle):
    casas = Casa.objects.filter(calle=nom_calle)
    return listacasas(request, casas, nom_calle)

def casadefault(request):
    id_prim = Casa.objects.all().first().casa_id
    #response = redirect('/' + id_prim)
    response = redirect('/listaclientes/')
    return response

def documentos(request, carpeta, archivo):
    usuario = request.user.username
    if usuario == "" or usuario is None:
        response = redirect('/accounts/login/')
        return response
    return redirect("https://storage.googleapis.com/ventasportones-261716.appspot.com/" + carpeta + "/" + archivo)

def error_cliente(request, cliente_id):
    cliente = Cliente.objects.get(pk=cliente_id)
    context = {
        "cliente": cliente,
        "usuario": usuario
    }
    return render(request, 'error/index.html', context)

def seguimientocliente(request):
    if request.method == "POST":
        form = ActualizacionClienteForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect("/")
    if 'idcliente' in request.session and request.session['idcliente'] != 0:
        cliente = Cliente.objects.get(pk=request.session['idcliente'])
        request.session['idcliente'] = 0
        form_act = ActualizacionClienteForm({'cliente': cliente, 'fecha':datetime.now(pytz.timezone('America/Mexico_City'))})
        context = {"form_act" : form_act}
        return render(request, 'seguimientocliente/registro.html', context)
    return redirect('/')

def listaseguimientocliente(request):
    if 'idcliente' in request.session and request.session['idcliente'] != 0:
        cliente = Cliente.objects.get(pk=request.session['idcliente'])
        request.session['idcliente'] = 0
        actuals = cliente.actualizaciones_por_cliente.all()
        #actuals = Actualizacion.objects.all()
        context = {
            'actualizaciones': actuals,
            "usuario": usuario
        }
        return render(request, 'seguimientocliente/seguimientolista.html', context)
    return redirect('/')
