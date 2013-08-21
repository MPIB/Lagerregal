from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from devices.models import Device, Room, Building, Manufacturer
from devicetypes.models import Type
from django.utils import simplejson
from django.core.urlresolvers import reverse
from main.models import DashboardWidget, widgets
from django.db.models import Max
from django.template.loader import render_to_string
from reversion.models import Version
import datetime
from django.contrib.contenttypes.models import ContentType

@dajaxice_register
def add_widget(request, widgetname):
    dajax = Dajax()
    if widgetname in widgets:
        userwidgets = DashboardWidget.objects.filter(user=request.user)
        if len(userwidgets.filter(widgetname=widgetname)) != 0:
            return dajax.json()
        widget = DashboardWidget()
        widget.column = "l"
        oldindex = userwidgets.filter(column="l").aggregate(Max('index'))["index__max"]
        widget.index = oldindex + 1 if oldindex != None else 1
        widget.widgetname = widgetname
        widget.user = request.user
        widget.save()
        context = {}
        context['revisions'] = Version.objects.filter(content_type_id=ContentType.objects.get(model='device').id).order_by("-pk")[:20]
        context['newest_devices'] = Device.objects.all().order_by("-pk")[:10]
        context["today"] = datetime.date.today()
        context["overdue"] = Device.objects.filter(currentlending__duedate__lt = context["today"]).order_by("currentlending__duedate")
        if widget.column == "l":
            col = ".dashboard-left"
        else:
            col = ".dashboard-right"
        dajax.append(col, "innerHTML", render_to_string('snippets/widgets/{}.html'.format(widgetname), context))
        dajax.script("$('#addWidgetModal').foundation('reveal', 'close');")
        dajax.remove(".addWidget[data-name={0}]".format(widgetname))
    return dajax.json()

@dajaxice_register
def remove_widget(request, widgetname):
    dajax = Dajax()
    print widgetname, widgets
    if widgetname in widgets:
        DashboardWidget.objects.get(user=request.user, widgetname=widgetname).delete()

        dajax.script("""$({0}).slideUp("fast", function() {{
            $(this).remove()
        }});""".format(widgetname))
        dajax.append("#widgetlist", "innerHTML", """<li><a href="#" data-name="{0}" class="addWidget">{1}</a></li>""".format(widgetname, unicode(widgets[widgetname])))
    return dajax.json()

@dajaxice_register
def toggle_minimized(request, widgetname):
    dajax = Dajax()
    if widgetname in widgets:
        w = DashboardWidget.objects.get(user=request.user, widgetname=widgetname)
        w.minimized = not w.minimized
        w.save()
        dajax.script("""$({0}).find( ".minimize" ).toggleClass( "icon-minus" ).toggleClass( "icon-plus" );
  $({0}).find( ".widget-content" ).slideToggle("fast");""".format(widgetname))
    return dajax.json()

@dajaxice_register
def move_widgets(request, userwidgets):
    dajax = Dajax()
    for widgetname, widgetattr in userwidgets.iteritems():
        if widgetname in widgets:
            w = DashboardWidget.objects.get(user=request.user, widgetname=widgetname)
            if w.index != widgetattr["index"] or w.column != widgetattr["column"]:
                w.index = widgetattr["index"]
                w.column = widgetattr["column"]
                w.save()
    return dajax.json()