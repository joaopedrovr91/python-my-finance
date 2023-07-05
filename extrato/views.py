from django.shortcuts import render, redirect
from perfil.models import Categoria,Conta
from .models import Valores
from django.contrib import messages
from django.contrib.messages import constants
from datetime import timedelta, datetime
from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from django.urls import reverse
from django.utils import timezone
from django.template.loader import render_to_string
import os 
from django.conf import settings
from weasyprint import HTML
from io import BytesIO

def novo_valor(request):
    if request.method == "GET":
        contas = Conta.objects.all()
        categorias = Categoria.objects.all() 
        return render(request, 'novo_valor.html', {'contas': contas, 'categorias': categorias})
    elif request.method == "POST":
        valor = request.POST.get('valor')
        categoria = request.POST.get('categoria')
        descricao = request.POST.get('descricao')
        data = request.POST.get('data')
        conta = request.POST.get('conta')
        tipo = request.POST.get('tipo')
        
        valores = Valores(
            valor=valor,
            categoria_id=categoria,
            descricao=descricao,
            data=data,
            conta_id=conta,
            tipo=tipo,
        )

        valores.save()

        conta = Conta.objects.get(id=conta)
        
        if tipo == 'E':
            conta.valor += int(valor)
            messages.add_message(request, constants.SUCCESS, 'Entrada cadastrada com sucesso')
        else:
            conta.valor -= int(valor)
            messages.add_message(request, constants.SUCCESS, 'Saída cadastrada com sucesso')

        conta.save()
        return redirect('/extrato/novo_valor')
    
def view_extrato(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()

    conta_get = request.GET.get('conta')
    categoria_get = request.GET.get('categoria')
    periodo_get = request.GET.get('periodo')

    valores = Valores.objects.all()

    if conta_get:
        valores = valores.filter(conta__id=conta_get)

    if categoria_get:
        valores = valores.filter(categoria__id=categoria_get)

    if periodo_get:
        if periodo_get == '1':
            data_inicio = timezone.now().date() - timedelta(days=7)
        elif periodo_get == '2':
            data_inicio = timezone.now().date() - timedelta(days=15)
        elif periodo_get == '3':
            data_inicio = timezone.now().date() - timedelta(days=30)
        else:
            data_inicio = None

        if data_inicio:
            valores = valores.filter(data__range=(data_inicio, timezone.now().date()))

    return render(request, 'view_extrato.html', {'valores': valores, 'contas': contas, 'categorias': categorias})


def reset_filtros(request):
    # Redirecionar para a página de visualização de extrato sem os parâmetros de filtro
    return HttpResponseRedirect(reverse('view_extrato'))

def exportar_pdf(request):
    valores = Valores.objects.filter(data__month=datetime.now().month)
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
    
    path_template = os.path.join(settings.BASE_DIR, 'templates/partials/extrato.html')
    path_output = BytesIO()

    template_render = render_to_string(path_template, {'valores': valores, 'contas': contas, 'categorias': categorias})
    HTML(string=template_render).write_pdf(path_output)

    path_output.seek(0)
    

    return FileResponse(path_output, filename="extrato.pdf")