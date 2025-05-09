from django import template

register = template.Library()

@register.filter
def clp_format(value):
    try:
        number = float(value)
        # Separa parte entera y decimal
        integer_part = "{:,.0f}".format(int(number))
        # Reemplaza comas por puntos (para miles) y elimina decimales
        return f"${integer_part.replace(',', '.')}"
    except (ValueError, TypeError):
        return f"${value}"