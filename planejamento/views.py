from django.shortcuts import render
from perfil.models import Categoria
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def definir_planejamento(request):
    categorias = Categoria.objects.all()
    return render(request,'definir_planejamento.html', {'categorias': categorias})

@csrf_exempt
def update_valor_categoria(request, id):
    novo_valor = json.load(request)['novo_valor']
    categoria = Categoria.objects.get(id=id)
    categoria.valor_planejamento = novo_valor
    categoria.save()
    return JsonResponse({'status': 'Sucesso'})

def ver_planejamento(request):
    categorias = Categoria.objects.all()
    total_gasto = sum(categoria.total_gasto() for categoria in categorias)
    total_planejamento = sum(categoria.valor_planejamento for categoria in categorias)
    total_percentual = int((total_gasto / total_planejamento) * 100 if total_planejamento != 0 else 0)
    return render(request, 'ver_planejamento.html', {
        'categorias': categorias,
        'total_gasto': total_gasto,
        'total_planejamento': total_planejamento,
        'total_percentual': total_percentual
    })

