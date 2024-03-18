from .models import CustomUser
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.http import HttpResponse

def is_operador(user):
    return hasattr(user, 'customuser') and user.customuser.is_operador()

def generate_pdf_venda(venda):
    # Mapeamento dos meses em inglês para português
    meses = {
        "January": "Janeiro",
        "February": "Fevereiro",
        "March": "Março",
        "April": "Abril",
        "May": "Maio",
        "June": "Junho",
        "July": "Julho",
        "August": "Agosto",
        "September": "Setembro",
        "October": "Outubro",
        "November": "Novembro",
        "December": "Dezembro"
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="venda_{venda.id}.pdf"'

    # Crie um objeto SimpleDocTemplate com um título personalizado
    doc = SimpleDocTemplate(response, pagesize=letter, title=f"Detalhes da Venda #{venda.id}")


    # Estilos
    styles = getSampleStyleSheet()
    style_heading = styles['Heading1']
    style_body = styles['BodyText']

    # Lista de conteúdo do PDF
    content = []

    # Adiciona o título "Detalhes da Venda"
    content.append(Paragraph(f"Detalhes da Venda #{venda.id}", style_heading))

    # Define um novo estilo de parágrafo em negrito
    style_bold = ParagraphStyle(name='BoldBodyText', parent=style_body)
    style_bold.fontName = 'Helvetica-Bold'

    mes_pt = meses[venda.data.strftime("%B")]
    # Adiciona os campos em negrito
    content.append(Paragraph(f"<b>Data:</b> {venda.data.strftime('%d')} de {mes_pt} de {venda.data.strftime('%Y às %H:%M')}", style_bold))
    content.append(Paragraph(f"<b>Status:</b> {venda.get_status_display()}", style_bold))
    content.append(Paragraph(f"<b>Operador Responsável:</b> {venda.operador.nome if venda.operador else 'N/A'}", style_bold))
    content.append(Paragraph(f"<b>Cliente:</b> {venda.cliente.nome if venda.cliente else 'N/A'}", style_bold))
    content.append(Paragraph(f"<b>Desconto:</b> R$ {venda.desconto:.2f}", style_bold))
    content.append(Paragraph(f"<b>Valor Total:</b> R$ {venda.valor_total:.2f}", style_bold))

    # Adiciona um espaço em branco
    content.append(Spacer(1, 12))

    # Adiciona a tabela de itens se houver itens, caso contrário, adiciona mensagem de venda sem itens
    if venda.itemvenda_set.exists():
        # Definição dos dados da tabela
        data = [["Produto", "Quantidade/Peso", "Preço Unitário", "Subtotal"]]
        for item in venda.itemvenda_set.all():
            produto_nome = item.produto_por_quantidade.nome if item.produto_por_quantidade else item.produto_por_peso.nome
            # Quebra o nome do produto se for muito longo
            produto_nome = produto_nome[:70] + (produto_nome[70:] and '...')
            data.append([produto_nome,
                         f"{item.quantidade}" if item.produto_por_quantidade else f"{item.peso_vendido} kg",
                         f"R$ {item.preco_unitario:.2f}",
                         f"R$ {item.subtotal:.2f}"])

        # Configuração da tabela
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Cor de fundo do cabeçalho
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Cor do texto do cabeçalho
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Centraliza o conteúdo da tabela
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fonte em negrito para o cabeçalho
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Preenchimento inferior do cabeçalho
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Cor de fundo das células
            ('GRID', (0, 0), (-1, -1), 1, colors.black)  # Adiciona a grade na tabela
        ])

        # Cria a tabela
        table = Table(data)
        table.setStyle(table_style)

        # Adiciona a tabela ao conteúdo do PDF
        content.append(table)

    else:
        content.append(Paragraph("Essa venda não possui itens.", style_body))

    # Adiciona o conteúdo ao PDF
    doc.build(content)

    return response
