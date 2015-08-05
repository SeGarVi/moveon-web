from django import template

register = template.Library()

@register.filter(is_safe=True)
def text_color_from_background(background_color):
    red = int(background_color[1:3], 16)
    green = int(background_color[3:5], 16)
    blue = int(background_color[5:7], 16)
    
    if ((red + green + blue)/3 > 128):
        return '#000000'
    else:
        return '#ffffff'