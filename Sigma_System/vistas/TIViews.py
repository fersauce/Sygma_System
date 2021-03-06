from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from Sigma_System.models import TipoDeItem, Fase, Item, AtribTipoDeItem


def administrarTI(request, idProyect, idFase):
    """
    Vista que se encarga de mostrar los TI de la fase.
    @type request: django.http.HttpRequest.
    @param request: Contiene la informacion sobre la solicitud de la pagina que lo llamo

    @type idProyect: string.
    @param idProyect: Contiene el id del proyecto sobre el cual se esta trabajando.

    @type idFase: string.
    @param idFase: Contiene el id de la fase sobre la cual se esta trabajando.

    @rtype django.shortcuts.render
    @return: AdministrarTI.html, pagina en la cual se trabaja con los TI de la fase.

    @author: Fernando Saucedo
    """
    permisos = request.session['permisos']
    fase = Fase.objects.get(pk=idFase)
    tiposItem = TipoDeItem.objects.filter(fase=fase)
    return render(request, 'AdministrarTI.html',
                  {'fase': fase, 'listaTI': tiposItem, 'pkProyecto': idProyect, 'permisos': permisos})


def altaTI(request, idProyect, idFase):
    """
    Vista que se encarga de dar de alta un TI en la fase.
    @type request: django.http.HttpRequest.
    @param request: Contiene la informacion sobre la solicitud de la pagina
    que lo llamo

    @type idProyect: string.
    @param idProyect: Contiene el id del proyecto sobre el cual se esta
    trabajando.

    @type idFase: string.
    @param idFase: Contiene el id de la fase sobre la cual se esta
    trabajando.

    @rtype django.shortcuts.render
    @return: AdministrarTI.html, pagina en la cual se trabaja con los TI de
    la fase; o a tialta.html

    @author: Fernando Saucedo
    """
    fase = Fase.objects.get(pk=idFase)
    if request.method == 'POST':
        nombre = request.POST['nombre']
        TI = TipoDeItem.objects.filter(fase=fase, nombre=nombre)
        TI = TI.first()
        if TI is not None:
            messages.error(request, 'El nombre de Tipo de item ya existe en '
                                    'esta fase del proyecto')
            return render(request, 'timodificar.html',
                          {'pkProyecto': idProyect, 'pkFase': idFase, 'tipoItem': TI})
        if request.POST['importar'] == 'True':
            importar = True
        else:
            importar = False
        id_user = request.user.id
        user = User.objects.get(id=id_user)
        usuario = user.usuario
        tipo = TipoDeItem.objects.create(
            fase=fase,
            usuario=usuario,
            nombre=request.POST['nombre'],
            descripcion=request.POST['descripcion'],
            importar=importar
        )
        tipo.codigo = 'SS_'+str(idProyect) + '_' + str(idFase) + '_' + str(tipo.pk)
        tipo.save()
        messages.success(request, 'Tipo de item creado con exito')
        return HttpResponseRedirect(reverse('sigma:adm_ti', args=(idProyect, idFase)))
    return render(request, 'tialta.html',
                  {'pkProyecto': idProyect, 'pkFase': idFase})


def modificarTI(request, idProyect, idFase, idTI):
    """
    Vista que realiza la modificacion de un tipo de item.
    @type request: django.http.HttpRequest.
    @param request: Contiene la informacion sobre la solicitud de la pagina
    que lo llamo

    @type idProyect: unicode.
    @param idProyect: Contiene el id del proyecto sobre el cual se esta
    trabajando.

    @type idFase: unicode.
    @param idFase: Contiene el id de la fase sobre la cual se esta
    trabajando.

    @type idTI: unicode.
    @param idTI: Contiene el id del Tipo de Item que se quiere modificar

    @rtype django.shortcuts.render
    @return: AdministrarTI.html, pagina en la cual se trabaja con los TI de
    la fase; o a timodificar.html, para realizar la correcta modificacion

    @author: Fernando Saucedo
    """
    TImodificado = TipoDeItem.objects.get(pk=idTI)
    fase = Fase.objects.get(pk=idFase)
    if request.method == 'POST':
        nombre = request.POST['nombre']
        TI = TipoDeItem.objects.exclude(nombre=nombre).filter(fase=fase)
        ti2 = TipoDeItem.objects.all()
        print ti2.__class__
        print TI.__class__
        for ti in ti2:
            print ti.nombre.__class__
            print nombre.__class__
            if ti != TImodificado:
                if ti.nombre.__str__() == nombre.__str__():
                    print 'hola'
                    messages.error(request,
                                   'El nombre de Tipo de item ya existe en el '
                                   'esta fase del proyecto')
                    return render(request, 'timodificar.html',
                                  {'pkProyecto': idProyect, 'pkFase': idFase,
                                   'tipoItem': TImodificado})
        item = Item.objects.filter(tipoItems=TImodificado)
        if item.__len__() > 0:
            messages.error(request, 'No se puede modificar, el tipo de item ya'
                                    'se encuentra instanciado')
        if request.POST['importar'] == 'True':
            importar = True
        else:
            importar = False

        TImodificado.nombre = request.POST['nombre']
        TImodificado.descripcion = request.POST['descripcion']
        TImodificado.importar = importar
        TImodificado.save()

        messages.success(request, 'Tipo de Item modificado con exito')
        return HttpResponseRedirect(
            '/ss/proyecto/' + str(idProyect) + '/fase/' + str(
                idFase) + '/tipoItem/')

    return render(request, 'timodificar.html',
                  {'pkProyecto': idProyect, 'pkFase': idFase,
                   'tipoItem': TImodificado})


def bajaTI(request, idProyect, idFase, idTI):
    """
    Vista que realiza la modificacion de un tipo de item.
    @type request: django.http.HttpRequest.
    @param request: Contiene la informacion sobre la solicitud de la pagina
    que lo llamo

    @type idProyect: unicode.
    @param idProyect: Contiene el id del proyecto sobre el cual se esta
    trabajando.

    @type idFase: unicode.
    @param idFase: Contiene el id de la fase sobre la cual se esta
    trabajando.

    @type idTI: unicode.
    @param idTI: Contiene el id del Tipo de Item que se quiere dar de baja

    @rtype django.shortcuts.render
    @return: AdministrarTI.html, pagina en la cual se trabaja con los TI de
    la fase

    @author: Fernando Saucedo
    """
    TIEliminado = TipoDeItem.objects.get(pk=idTI)
    itemsInstanciados = Item.objects.filter(tipoItems=TIEliminado)
    if request.method == 'GET':
        if itemsInstanciados.__len__() > 0:
            messages.error(request, 'No se puede suprimir este tipo de item, ya'
                                    'se encuentra instanciado')
            return administrarTI(request, idProyect, idFase)
        try:
            TIEliminado.delete()
            messages.success(request, 'Tipo de Item ' + str(
                TIEliminado.nombre) + ' eliminado')
        except Exception as error:
            messages.error(request,
                           'Ha ocurrido un error en el sistema, el tipo'
                           'de item no ha podido ser eliminado')
            print error.args
            return administrarTI(request, idProyect, idFase)
    return administrarTI(request, idProyect, idFase)


def importarTI(request, idFase):
    """
    Vista que se encarga de importar el Tipo de Item selccionado
    @type request: django.http.HttpRequest.
    @param request: Contiene la informacion sobre la solicitud de la pagina
    que lo llamo

    @type idFase: unicode.
    @param idFase: Contiene el id de la fase sobre la cual se esta
    trabajando.

    @rtype django.shortcuts.render
    @return: AdministrarTI.html, pagina en la cual se trabaja con los TI de
    la fase

    @author: Fernando Saucedo
    """
    listaImportados = TipoDeItem.objects.filter(importar=True)
    for lista in listaImportados:
        print lista.nombre
    print idFase
    fase = Fase.objects.get(pk=idFase)
    id_user = request.user.id
    user = User.objects.get(id=id_user)
    usuario = user.usuario
    if request.method == 'POST':
        tiAImportar = TipoDeItem.objects.get(pk=request.POST['ti'])
        listaTIFase = TipoDeItem.objects.filter(fase=fase).exclude(
            pk=tiAImportar.pk)
        for ti in listaTIFase:
            if ti.nombre == request.POST['nombre']:
                messages.error(request, 'Este nombre ya esta siendo utilizado, '
                                        'por favor, cambielo.')
                return render(request, 'faseintercambiar.html',
                              {'fase': fase, 'tipos': listaImportados})
        tiNuevo = TipoDeItem.objects.create(
            fase=fase,
            usuario=usuario,
            nombre=request.POST['nombre'],
            descripcion=request.POST['descripcion'],
            importar=request.POST['importar']
        )
        tiNuevo.codigo = 'SS_' + str(fase.proyecto.pk) + '_' + str(
            idFase) + '_' + str(tiNuevo.pk)
        tiNuevo.save()
        listaAtributos = AtribTipoDeItem.objects.filter(tipoDeItem=tiAImportar)
        for atrib in listaAtributos:
            atributo = AtribTipoDeItem()
            atributo.tipoDeItem = tiNuevo
            atributo.atributos = atrib.atributos
            atributo.nombre = atrib.nombre
            atributo.save()
        messages.success(request, 'tipo importado correctamente')
    else:
        messages.success(request, 'hola')
        return render(request, 'faseintercambiar.html',
                      {'fase': fase, 'tipos': listaImportados})
    return HttpResponseRedirect(
        '/ss/proyecto/' + str(fase.proyecto.pk) + '/fase/' + str(
            fase.pk) + '/tipoItem/')