from django.shortcuts import render, redirect
from perfil.models import Categoria
from .models import ContaPagar, ContaPaga
from django.contrib.messages import constants
from django.contrib import messages
from datetime import datetime


def definir_contas(request):
    if request.method == "GET":
        categorias = Categoria.objects.all()
        return render(request, 'definir_contas.html', {'categorias': categorias})
    else:
        titulo = request.POST.get('titulo')
        categoria = request.POST.get('categoria')
        descricao = request.POST.get('descricao')
        valor = request.POST.get('valor')
        dia_pagamento = request.POST.get('dia_pagamento')

        conta = ContaPagar(
            titulo=titulo,
            categoria_id=categoria,
            descricao=descricao,
            valor=valor,
            dia_pagamento=dia_pagamento
        )

        conta.save()

        messages.add_message(request, constants.SUCCESS, 'Conta cadastrada com sucesso')

        return redirect('/contas/definir_contas')

def ver_contas(request):
    MES_ATUAL = datetime.now().month
    DIA_ATUAL = datetime.now().day
    
    meses_pt = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro"
    }

    nome_mes = meses_pt[MES_ATUAL]

    contas = ContaPagar.objects.all()
    contas_pagas = ContaPaga.objects.filter(data_pagamento__month = MES_ATUAL).values('conta')
    contas_vencidas = contas.filter(dia_pagamento__lt=DIA_ATUAL).exclude(id__in=contas_pagas)
    contas_proximas_vencimento = contas.filter(dia_pagamento__lte = DIA_ATUAL + 5).filter(dia_pagamento__gte=DIA_ATUAL).exclude(id__in=contas_pagas)
    restantes = contas.exclude(id__in=contas_vencidas).exclude(id__in=contas_proximas_vencimento).exclude(id__in=contas_pagas)


    quantidade_contas_vencidas = contas_vencidas.count()
    quantidade_contas_pagas = contas_pagas.count()
    quantidade_contas_proximas_vencimento = contas_proximas_vencimento.count()
    quantidade_restantes = restantes.count()
    return render(request, 'ver_contas.html', {'contas_vencidas': contas_vencidas, 
                                               'contas_proximas_vencimento': contas_proximas_vencimento, 
                                               'restantes': restantes,
                                               'quantidade_contas_vencidas': quantidade_contas_vencidas,
                                               'quantidade_contas_pagas': quantidade_contas_pagas,
                                               'quantidade_contas_proximas_vencimento': quantidade_contas_proximas_vencimento,
                                               'quantidade_restantes': quantidade_restantes,
                                               'MES_ATUAL': MES_ATUAL,
                                               'nome_mes': nome_mes})

def pagar_conta(request, conta_id):
    conta = ContaPagar.objects.get(id=conta_id)
    ContaPaga.objects.create(conta=conta, data_pagamento=datetime.now())
    return redirect('ver_contas')
