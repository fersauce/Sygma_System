__author__ = 'ruth'
from random import choice
import string
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMessage
from django.shortcuts import render, render_to_response
from django.http import *
from django.template import RequestContext
from django.template.loader import render_to_string
from Sigma_System.models import *
from Sigma_System.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required(login_url='/login/')
def administrarItem(request, idFase):
    request.session['fase'] = idFase

    fs = Fase.objects.get(pk=idFase)
    nameFa = fs.nombre

    proy=fs.proyecto


    permisos=request.session['permisos']
    its = Item.objects.exclude(estado='baja', tipoItems__fase=fs)
    return render(request, 'AdministrarItem.html',
                  {'items': its, 'fase': fs,
                   'username': request.user.username,
                   'proy':proy, 'permisos':permisos})


@login_required(login_url='/login/')
def altaItem(request, idFase):
    """
    vista utilizada para crear un item
    """
    its = Item.objects.exclude(estado='baja')

    tis = TipoDeItem.objects.filter(fase=Fase.objects.get(pk=idFase))
    fase = Fase.objects.get(pk=idFase)
    print(fase.nombre)
    print tis.first().__getattribute__('nombre')
    if request.method == 'POST':
        try:
            ti = TipoDeItem.objects.get(id=request.POST['tipo'])

            name = request.POST['nombre']
            versionA = 1
            compl = request.POST['complejidad']
            pri = request.POST['prior']
            est = "activo"
            itt = Item.objects.create(
                tipoItems=ti,
                nombre=name,
                version=versionA,
                complejidad=compl,
                prioridad=pri,
                estado=est
            )
            historial = Historial.objects.create(
                item=itt,
                nro_version_act=1,
                nro_version_ant=0,
                cod_mod="a",
                valor_act=0,
                valor_ant=0,
                descripcion="alta",
                fecha_mod=datetime.datetime.now()
            )
            print historial.pk
            messages.success(request,
                             'El item "' + name + '" ha sido creado con exito')
        except Exception:
            messages.error(request, 'Ocurrio un error.')
    else:
        return render(request, 'AltaItems.html',
                      {'tipos': tis, 'fase': idFase, 'username': request.user.username})

    return render(request, 'AdministrarItem.html',
                  {'items': its, 'fase': idFase, 'username': request.user.username})


@login_required(login_url='/login/')
def modificar_item(request, it):
    """
    vista utilizada para modificar un item
    donde el parametro it es el id del item


    """

    its = Item.objects.get(id=it)
    if request.method == 'POST':
        print(it)
        nAct = its.nombre
        comAct = its.complejidad
        priAct = its.prioridad
        vAct = its.version
        estAct = its.estado

        nNuevo = request.POST['nombre']
        comNuevo = request.POST['complejidad']
        priNuevo = request.POST['prior']
        estNuevo = request.POST['estado']
        print "nombre", nNuevo
        print "complejidad", comNuevo
        print "prioridad", priNuevo
        print "estado", estNuevo

        its.nombre = request.POST['nombre']
        its.complejidad = request.POST['complejidad']
        its.prioridad = request.POST['prior']

        vers = its.version + 1
        vNuevo = vers
        its.version = vers
        its.estado = request.POST['estado']

        its.save()
        messages.info(request, 'Item modificado correctamente')

        if nAct != nNuevo:
            print("entro en el if de nombre")
            Historial.objects.create(
                item=its,
                nro_version_act=vNuevo,
                nro_version_ant=vAct,
                cod_mod="m",
                valor_act=nNuevo,
                valor_ant=nAct,
                descripcion="nombre",
                fecha_mod=datetime.datetime.now()
            )
        print request.POST['complejidad']
        if comAct == int(comNuevo):
            print("entro en el if de complejidad")
            print("complejidad1", comAct)
            print('complejidad2', comNuevo)
        else:
            Historial.objects.create(
                item=its,
                nro_version_act=vNuevo,
                nro_version_ant=vAct,
                cod_mod="m",
                valor_act=comNuevo,
                valor_ant=comAct,
                descripcion="complejidad",
                fecha_mod=datetime.datetime.now()
            )

        if priAct == int(priNuevo):
            print("entro en el if de pri")
        else:
            Historial.objects.create(
                item=its,
                nro_version_act=vNuevo,
                nro_version_ant=vAct,
                cod_mod="m",
                valor_act=priNuevo,
                valor_ant=priAct,
                descripcion="prioridad",
                fecha_mod=datetime.datetime.now()
            )
        if estAct != estNuevo:
            print("entro en el if de estado")
            Historial.objects.create(
                item=its,
                nro_version_act=vNuevo,
                nro_version_ant=vAct,
                cod_mod="m",
                valor_act=estNuevo,
                valor_ant=estAct,
                descripcion="estado",
                fecha_mod=datetime.datetime.now()
            )

    else:
        return render(request, 'ModificarItem.html', {'item': its, 'username': request.user.username})
    return HttpResponseRedirect('/ss/adm_i/' + str(its.tipoItems.fase.pk))


@login_required(login_url='/login/')
def baja_item(request, it):
    """
    vista utilizada para dar de baja un item, baja logica
    donde el parametro it es el id del item a dar de baja
    """
    #user = User.objects.get(id=us)

    its = Item.objects.get(id=it)
    estAct = its.estado
    its.estado = "baja"
    verActual = its.version
    nVersion = verActual + 1
    its.version = nVersion

    its.save()
    messages.error(request, 'El item  ha sido eliminado')

    Historial.objects.create(
        item=its,
        nro_version_act=nVersion,
        nro_version_ant=verActual,
        cod_mod="b",
        valor_act="baja",
        valor_ant=estAct,
        descripcion="baja",
        fecha_mod=datetime.datetime.now()
    )

    return HttpResponseRedirect('/ss/adm_i/' + str(its.tipoItems.fase.pk))


@login_required(login_url='/login/')
def revivir_item(request, idFase):
    """
    vista utilizada para mostrar los items a ser revividos

    """
    request.session['fase'] = idFase

    fs = Fase.objects.get(pk=idFase)
    nameFa = fs.nombre
    its = Item.objects.filter(estado='baja')

    return render(request, 'RevivirItem.html',
                  {'items': its, 'fase': idFase, 'nomb': nameFa, 'username': request.user.username})


@login_required(login_url='/login/')
def revivir(request, it):
    """
    vista utilizada para revivir un item eliminado
    donde el parametro it es el id del item a revivir
    """
    #user = User.objects.get(id=us)
    its = Item.objects.get(id=it)
    its.estado = "activo"
    verActual = its.version
    verNuevo = verActual + 1
    its.version = verNuevo
    its.save()
    messages.success(request, 'El item  ha sido revivido')

    Historial.objects.create(
        item=its,
        nro_version_act=verNuevo,
        nro_version_ant=verActual,
        cod_mod="rev",
        valor_act="activo",
        valor_ant="baja",
        descripcion="revivir",
        fecha_mod=datetime.datetime.now()
    )

    return HttpResponseRedirect('/ss/adm_i_rev/' + str(its.tipoItems.fase.pk))


@login_required(login_url='/login/')
def revertir(request, idFase):
    """
    vista utilizada para mostrar las versiones del item a reversionar

    """

    itemAux = Item.objects.get(id=idFase)
    tipo = itemAux.tipoItems
    fase = tipo.fase
    nameFa = fase.nombre
    idf = fase.pk  # Fase.objects.get(nombre=nameFa)
    histor = Historial.objects.filter(item=idFase)

    return render(request, 'RevertirItem.html',
                  {'hist': histor, 'fase': idf, 'nomb': nameFa,
                   'items': itemAux, 'username': request.user.username})


@login_required(login_url='/login/')
def revertirItem(request, idItem, versionRev, idHis):
    """
    vista utilizada para realizar la reversion del item,
    idItem es el id del item que se va a cambiar
    verisonRev es la version a la que ira nuevamente
    historial.item.all

    """

    its = Item.objects.get(id=idItem)
    versionActual = its.version

    his2 = Historial.objects.get(id=idHis)

    his1 = Historial.objects.filter(item=its)
    for h in his1:
        if h.nro_version_act == versionActual:
            idHisFinal = h.id

    idHisRev = his2.id

    ultimo = idHisFinal
    indice = ultimo + 1
    print('id historial rever', idHisRev)
    print('id historial ultimo', ultimo)
    print('reversion', versionRev)
    print('ver actual', versionActual)
    if int(versionRev) < int(versionActual):
        print('entro en la rev es menor a la ver actual')
        for i in range(idHisRev, ultimo):
            print('for')
            indice = indice - 1
            print(indice)
            historialAux = Historial.objects.get(id=indice)
            itemAuxiliar = historialAux.item
            idLeido = itemAuxiliar.id
            print 'id leido', idLeido
            print 'idParametro', idItem

            if (int(idLeido) == int(idItem)):
                print('id son iguales')
                if int(historialAux.nro_version_act) <= int(versionActual):
                    print 'version menor', historialAux.nro_version_act
                    print int(historialAux.nro_version_act)
                    print int(versionRev)
                    if int(historialAux.nro_version_act) == int(versionRev):
                        print('reversion encontrada')
                        if historialAux.cod_mod == 'm':
                            if historialAux.descripcion == 'nombre':
                                valorActualEnHistorial = historialAux.valor_act
                                valorAnteriorEnHistorial = historialAux.valor_ant
                                its.nombre = valorActualEnHistorial
                                its.version = versionRev
                                its.save()
                                Historial.objects.create(
                                    item=its,
                                    nro_version_act=versionActual + 1,
                                    nro_version_ant=versionRev,
                                    cod_mod="revertir",
                                    valor_act=versionRev,
                                    valor_ant=versionActual,
                                    descripcion="reversion",
                                    fecha_mod=datetime.datetime.now()
                                )

                                messages.info(request, 'Item reversionado')
                            if historialAux.descripcion == 'complejidad':
                                print('reversion a un cambio de complejidad')
                                valorActualEnHistorial = historialAux.valor_act
                                valorAnteriorEnHistorial = historialAux.valor_ant
                                its.complejidad = valorActualEnHistorial
                                its.version = versionRev
                                its.save()

                                Historial.objects.create(
                                    item=its,
                                    nro_version_act=versionActual + 1,
                                    nro_version_ant=versionRev,
                                    cod_mod="revertir",
                                    valor_act=versionRev,
                                    valor_ant=versionActual,
                                    descripcion="reversion",
                                    fecha_mod=datetime.datetime.now()
                                )

                                messages.info(request, 'Item reversionado')
                            if historialAux.descripcion == 'prioridad':
                                valorActualEnHistorial = historialAux.valor_act
                                valorAnteriorEnHistorial = historialAux.valor_ant
                                its.prioridad = valorActualEnHistorial
                                its.version = versionRev
                                its.save()

                                Historial.objects.create(
                                    item=its,
                                    nro_version_act=versionActual + 1,
                                    nro_version_ant=versionRev,
                                    cod_mod="revertir",
                                    valor_act=versionRev,
                                    valor_ant=versionActual,
                                    descripcion="reversion",
                                    fecha_mod=datetime.datetime.now()
                                )

                                messages.info(request, 'Item reversionado')

                            if historialAux.descripcion == 'estado':
                                valorActualEnHistorial = historialAux.valor_act
                                valorAnteriorEnHistorial = historialAux.valor_ant
                                its.estado = valorActualEnHistorial
                                its.version = versionRev
                                its.save()

                                Historial.objects.create(
                                    item=its,
                                    nro_version_act=versionActual + 1,
                                    nro_version_ant=versionRev,
                                    cod_mod="revertir",
                                    valor_act=versionRev,
                                    valor_ant=versionActual,
                                    descripcion="reversion",
                                    fecha_mod=datetime.datetime.now()
                                )

                                messages.info(request, 'Item reversionado')
                        if versionActual == 1:
                            messages.error(request,
                                           'Item no tiene version anterior, no puede reversionarse')
                        if historialAux.cod_mod == 'b':
                            its.estado = 'baja'
                            its.version = versionRev
                            its.save()
                            Historial.objects.create(
                                item=its,
                                nro_version_act=versionActual + 1,
                                nro_version_ant=versionRev,
                                cod_mod="revertir",
                                valor_act=versionRev,
                                valor_ant=versionActual,
                                descripcion="reversion",
                                fecha_mod=datetime.datetime.now()
                            )

                            messages.info(request, 'Item reversionado')
                    else:


                        print 'entro en el si no'
                        if historialAux.cod_mod == 'm':
                            if historialAux.descripcion == 'nombre':
                                valorActualEnHistorial = historialAux.valor_act
                                valorAnteriorEnHistorial = historialAux.valor_ant
                                its.nombre = valorAnteriorEnHistorial
                                its.version = versionRev
                                its.save()
                            if historialAux.descripcion == 'complejidad':
                                print('reversion a un cambio de complejidad')
                                valorActualEnHistorial = historialAux.valor_act
                                valorAnteriorEnHistorial = historialAux.valor_ant
                                its.complejidad = valorAnteriorEnHistorial
                                its.version = versionRev
                                its.save()
                            if historialAux.descripcion == 'prioridad':
                                valorActualEnHistorial = historialAux.valor_act
                                valorAnteriorEnHistorial = historialAux.valor_ant
                                its.prioridad = valorAnteriorEnHistorial
                                its.version = versionRev
                                its.save()
                            if historialAux.descripcion == 'estado':
                                valorActualEnHistorial = historialAux.valor_act
                                valorAnteriorEnHistorial = historialAux.valor_ant
                                its.estado = valorAnteriorEnHistorial
                                its.version = versionRev
                                its.save()

    """
    if versionRev > versionActual:
        indice=idHisRev-1
        for i in range(idHisRev,ultimo):
            print('for')
            indice=indice+1
            print(indice)
            historialAux=Historial.objects.get(id=indice)
            itemAuxiliar=historialAux.item
            idLeido=itemAuxiliar.id
            print 'id leido', idLeido
            print 'idParametro', idItem

            if (int(idLeido) == int(idItem)):
                print('id son iguales')
                if int(historialAux.nro_version_act)>=int(versionActual):
                    print 'version menor',historialAux.nro_version_act
                    print int(historialAux.nro_version_act)
                    print int(versionRev)
                    if int(historialAux.nro_version_act)== int(versionRev):
                        print('reversion encontrada')
                        if historialAux.cod_mod =='m':
                            if historialAux.descripcion== 'nombre':

                                valorActualEnHistorial=historialAux.valor_act
                                valorAnteriorEnHistorial=historialAux.valor_ant
                                its.nombre=valorActualEnHistorial
                                its.version=versionRev
                                its.save()
                                hi=Historial.objects.create(
                                    item=its,
                                    nro_version_act = versionActual+1,
                                    nro_version_ant = versionRev,
                                    cod_mod = "revertir",
                                    valor_act =  versionRev,
                                    valor_ant =  versionActual,
                                    descripcion = "reversion",
                                    fecha_mod = datetime.datetime.now()
                                     )
                                hi.save()
                                messages.success(request, 'Item reversionado')
                            if historialAux.descripcion =='complejidad':
                                print('reversion a un cambio de complejidad')
                                valorActualEnHistorial=historialAux.valor_act
                                valorAnteriorEnHistorial=historialAux.valor_ant
                                its.complejidad=valorActualEnHistorial
                                its.version=versionRev
                                its.save()

                                hi=Historial.objects.create(
                                    item=its,
                                    nro_version_act = versionActual+1,
                                    nro_version_ant = versionRev,
                                    cod_mod = "revertir",
                                    valor_act = versionRev,
                                    valor_ant = versionActual,
                                    descripcion = "reversion",
                                    fecha_mod = datetime.datetime.now()
                                )
                                hi.save()
                                messages.success(request, 'Item reversionado')
                            if historialAux.descripcion =='prioridad':
                                valorActualEnHistorial=historialAux.valor_act
                                valorAnteriorEnHistorial=historialAux.valor_ant
                                its.prioridad=valorActualEnHistorial
                                its.version=versionRev
                                its.save()

                                hi=Historial.objects.create(
                                    item=its,
                                    nro_version_act = versionActual+1,
                                    nro_version_ant = versionRev,
                                    cod_mod = "revertir",
                                    valor_act = versionRev,
                                    valor_ant = versionActual,
                                    descripcion = "reversion",
                                    fecha_mod = datetime.datetime.now()
                                )
                                hi.save()
                                messages.success(request, 'Item reversionado')

                            if historialAux.descripcion =='estado':
                                valorActualEnHistorial=historialAux.valor_act
                                valorAnteriorEnHistorial=historialAux.valor_ant
                                its.estado=valorActualEnHistorial
                                its.version=versionRev
                                its.save()

                                hi=Historial.objects.create(
                                    item=its,
                                    nro_version_act = versionActual+1,
                                    nro_version_ant = versionRev,
                                    cod_mod = "revertir",
                                    valor_act = versionRev,
                                    valor_ant = versionActual,
                                    descripcion = "reversion",
                                    fecha_mod = datetime.datetime.now()
                                )

                                messages.success(request, 'Item reversionado')
                        if versionActual ==1:
                             messages.error(request, 'Item no tiene version anterior, no puede reversionarse')
                        if historialAux.cod_mod=='b':
                            its.estado='baja'
                            its.version=versionRev
                            its.save()
                            Historial.objects.create(
                                    item=its,
                                    nro_version_act = versionActual+1,
                                    nro_version_ant = versionRev,
                                    cod_mod = "revertir",
                                    valor_act = versionRev,
                                    valor_ant = versionActual,
                                    descripcion = "reversion",
                                    fecha_mod = datetime.datetime.now()
                            )

                            messages.success(request, 'Item reversionado')
                    else:
                        print 'entro en el si no'
                        if historialAux.cod_mod =='m':
                            if historialAux.descripcion== 'nombre':

                                valorActualEnHistorial=historialAux.valor_act
                                valorAnteriorEnHistorial=historialAux.valor_ant
                                its.nombre=valorAnteriorEnHistorial
                                its.version=versionRev
                                its.save()
                            if historialAux.descripcion =='complejidad':
                                print('reversion a un cambio de complejidad')
                                valorActualEnHistorial=historialAux.valor_act
                                valorAnteriorEnHistorial=historialAux.valor_ant
                                its.complejidad=valorAnteriorEnHistorial
                                its.version=versionRev
                                its.save()
                            if historialAux.descripcion =='prioridad':
                                valorActualEnHistorial=historialAux.valor_act
                                valorAnteriorEnHistorial=historialAux.valor_ant
                                its.prioridad=valorAnteriorEnHistorial
                                its.version=versionRev
                                its.save()
                            if historialAux.descripcion =='estado':
                                valorActualEnHistorial=historialAux.valor_act
                                valorAnteriorEnHistorial=historialAux.valor_ant
                                its.estado=valorAnteriorEnHistorial
                                its.version=versionRev
                                its.save()
"""

    return HttpResponseRedirect('/ss/adm_i/' + str(its.tipoItems.fase.pk))


@login_required(login_url='/login/')
def historialItem(request, idItem):
    """
    vista utilizada para mostrar el historial del item

    """

    its = Item.objects.get(id=idItem)
    fase = its.tipoItems.fase
    his1 = Historial.objects.filter(item__pk=its.pk)
    for hi in his1:
        print hi.descripcion

    return render(request, 'HistorialItem.html',
                  {'his': his1, 'item': its, 'fase': fase})

